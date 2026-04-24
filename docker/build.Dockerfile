# syntax=docker/dockerfile:1

# ============================================================================
# Base image tag (set via docker-compose or build.py)
# ============================================================================
ARG BASE_IMAGE_TAG=base

# ============================================================================
# STAGE 1: build-python
# Compiles Python from source with optimizations and installs base packages
# ============================================================================

FROM ghcr.io/corbel-spatial/here-be-dragons:${BASE_IMAGE_TAG} AS build-python

ARG PARALLEL
ARG PYTHON_VER

ENV HOME=/root \
    DEBIAN_FRONTEND=noninteractive
WORKDIR $HOME

# Install Python build dependencies
RUN apt update && \
    apt install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        cmake \
        curl \
        git \
        libncurses-dev \
        libreadline-dev \
        libssl-dev \
        libzstd-dev \
        lzma \
        ninja-build \
        pkg-config \
        sqlite3 \
        tk-dev \
        zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*

# Compile CPython from source with optimizations
# Flags: --enable-optimizations (PGO), --with-lto (Link-Time Optimization)
RUN git clone --depth 1 --branch $PYTHON_VER --single-branch https://github.com/python/cpython && \
    cd $HOME/cpython && \
    ./configure --enable-optimizations --with-lto --enable-loadable-sqlite-modules && \
    make -j $PARALLEL && \
    make install && \
    strip --strip-all /usr/local/bin/python* 2>/dev/null || true && \
    strip --strip-all /usr/local/lib/libpython* 2>/dev/null || true && \
    cd / && \
    rm -rf $HOME/cpython $HOME/.cache

# Install uv (fast Python package installer)
RUN pip3 install --no-cache-dir uv --root-user-action ignore && \
    strip --strip-all /usr/local/bin/uv 2>/dev/null || true

# Install core Python packages (no-binary for local optimization)
RUN uv pip install --system --no-cache-dir certifi numpy setuptools && \
    uv pip install --system --no-cache-dir pyproj shapely --no-binary :all: && \
    python3 -c "import numpy; print('NumPy version:', numpy.__version__); print('BLAS info:', numpy.show_config())"

# ============================================================================
# STAGE 2: build-gdal
# Compiles GDAL (geospatial data abstraction library)
# ============================================================================

FROM build-python AS build-gdal

ARG GDAL_VER
ARG PARALLEL

ENV HOME=/root \
    DEBIAN_FRONTEND=noninteractive
WORKDIR $HOME

# Install GDAL build dependencies
RUN apt update && \
    apt install -y --no-install-recommends \
        cmake \
        curl \
        git \
        ninja-build && \
    rm -rf /var/lib/apt/lists/*

# Compile GDAL from source with LTO and debug info removal
RUN git clone --depth 1 --branch $GDAL_VER --single-branch https://github.com/OSGeo/gdal && \
    mkdir $HOME/gdal/build && \
    cd $HOME/gdal/build && \
    cmake -G Ninja \
        .. \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INTERPROCEDURAL_OPTIMIZATION=ON \
        -DCMAKE_C_FLAGS_RELEASE="-g0" \
        -DCMAKE_CXX_FLAGS_RELEASE="-g0" && \
    ninja -j $PARALLEL install && \
    ldconfig && \
    find /usr/local/lib -name "libgdal*" -exec strip --strip-all {} \; 2>/dev/null || true && \
    find /usr/local/bin -name "gdal*" -exec strip --strip-all {} \; 2>/dev/null || true && \
    cd / && \
    rm -rf $HOME/gdal $HOME/.cache

# Verify GDAL installation
RUN python3 -c "from osgeo import gdal"

# ============================================================================
# STAGE 3: build-arrow
# Compiles Apache Arrow C++ library with Python bindings
# ============================================================================

FROM build-gdal AS build-arrow

ARG ARROW_VER
ARG PARALLEL

ENV HOME=/root \
    DEBIAN_FRONTEND=noninteractive \
    ARROW_DIR=$HOME/arrow \
    ARROW_HOME=$HOME/arrow/dist \
    LD_LIBRARY_PATH=$HOME/arrow/dist/lib \
    CMAKE_PREFIX_PATH=$HOME/arrow/dist \
    PYARROW_PARALLEL=$PARALLEL \
    PYARROW_BUNDLE_ARROW_CPP=1 \
    PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1

WORKDIR $HOME

# Install Arrow build dependencies
RUN apt update && \
    apt install -y --no-install-recommends \
        cmake \
        curl \
        git \
        ninja-build && \
    rm -rf /var/lib/apt/lists/*

# Compile Apache Arrow C++ and Python bindings with LTO
RUN git clone --depth 1 --branch $ARROW_VER --single-branch https://github.com/apache/arrow && \
    mkdir $ARROW_HOME && \
    cd $ARROW_HOME && \
    uv pip install --system --no-cache-dir -r $ARROW_DIR/python/requirements-build.txt && \
    cmake -S $ARROW_DIR/cpp -B $ARROW_DIR/cpp/build \
        -DCMAKE_INSTALL_PREFIX=$ARROW_HOME \
        -DCMAKE_INSTALL_LIBDIR=lib \
        -DCMAKE_INTERPROCEDURAL_OPTIMIZATION=ON \
        -DCMAKE_C_FLAGS_RELEASE="-g0" \
        -DCMAKE_CXX_FLAGS_RELEASE="-g0" \
        --preset ninja-release-python && \
    cmake --build $ARROW_DIR/cpp/build --target install --parallel $PARALLEL && \
    ldconfig && \
    strip --strip-all $ARROW_HOME/lib/libarrow* 2>/dev/null || true && \
    cd $ARROW_DIR/python && \
    uv pip install --system --no-cache-dir . && \
    cd / && \
    rm -rf $HOME/arrow $HOME/.cache

# Install geoarrow and verify Arrow installation
RUN uv pip install --system --no-cache-dir geoarrow-pyarrow --no-binary :all: && \
    python3 -c "import pyarrow" && \
    python3 -c "import geoarrow.pyarrow"

# ============================================================================
# STAGE 4: install-gis
# Installs additional geospatial and data packages
# ============================================================================

FROM build-arrow AS install-gis

# Install additional GIS and data packages
RUN uv pip install --system --no-cache-dir fiona geoalchemy2 geopandas geopy mapclassify psycopg psycopg2 || echo "WARNING: Extra packages did not build"

# Clear uv cache
RUN uv cache clean

# ============================================================================
# STAGE 5: runtime
# Final production image with all dependencies and optimizations
# ============================================================================

FROM install-gis AS runtime

# Set OpenBLAS to single-threaded to prevent over-threading in containers
ENV OPENBLAS_NUM_THREADS=1

# Pre-compile all Python modules to bytecode for faster first-import
# Then purge build tools, clean package metadata, strip symbols, and remove build artifacts
RUN python3 -m py_compile $(find /usr/local/lib/python*/site-packages -name "*.py" -type f 2>/dev/null) 2>/dev/null || true && \
    apt-get update && \
    apt-get purge -y \
        build-essential \
        ca-certificates \
        cmake \
        curl \
        git \
        libncurses-dev \
        libreadline-dev \
        libssl-dev \
        libzstd-dev \
        lzma \
        ninja-build \
        pkg-config \
        python3-dev \
        sqlite3 \
        tk-dev \
        zlib1g-dev && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    find /usr/local/lib/python*/site-packages -type d -name "*.dist-info" -exec rm -rf {} + 2>/dev/null || true && \
    find /usr/local/lib/python*/site-packages -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true && \
    find /usr/local/lib/python*/site-packages -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true && \
    find /usr/local/lib/python*/site-packages -name "*.so" -exec strip --strip-unneeded {} \; 2>/dev/null || true && \
    find /usr/local/lib/python*/site-packages -name "*.so.debug" -delete 2>/dev/null || true && \
    find /usr/local/lib/python*/site-packages -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true && \
    find /usr/local/lib/python*/site-packages -type f -name "*.pyc" -delete && \
    find /usr/local/lib/python*/site-packages -name "*.h" -delete 2>/dev/null || true && \
    find /usr/local/lib/python*/site-packages \( -name "conftest.py" -o -name "pytest.ini" -o -name "setup.cfg" \) -type f -delete 2>/dev/null || true && \
    find /usr/local/lib/python*/site-packages \( -name "*.c" -o -name "*.cpp" \) -type f -delete 2>/dev/null || true && \
    find /usr/local/lib -type d -name "cmake" -exec rm -rf {} + 2>/dev/null || true

# Create Python symlinks for convenience
RUN ln -sf /usr/local/bin/python3 /usr/bin/python && \
    ln -sf /usr/local/bin/pip3 /usr/local/bin/pip && \
    ln -sf /usr/local/bin/pip3 /usr/bin/pip

# Finalize runtime setup and verify all key libraries
RUN ldconfig && \
    python -c "from osgeo import gdal" && \
    python -c "import pyarrow" && \
    python -c "import geoarrow.pyarrow"

# Install pixi package manager
RUN curl -fsSL https://pixi.sh/install.sh | sh
ENV PATH=$HOME/.pixi/bin:$PATH
RUN pixi self-update

CMD ["bash"]
