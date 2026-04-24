# syntax=docker/dockerfile:1

# ============================================================================
# STAGE 1: build-python
# ============================================================================

ARG BASE_IMAGE_TAG=base
ARG NAMESPACE=localhost/

FROM ${NAMESPACE}here-be-dragons:${BASE_IMAGE_TAG} AS build-python

ARG PARALLEL
ARG PYTHON_VER

ENV HOME=/root \
    DEBIAN_FRONTEND=noninteractive
WORKDIR $HOME

RUN apt update && \
    apt install -y --no-install-recommends \
        autoconf \
        automake \
        build-essential \
        ca-certificates \
        cmake \
        curl \
        git \
        libncurses-dev \
        libpq-dev \
        libreadline-dev \
        libssl-dev \
        libtool \
        libzstd-dev \
        lzma \
        ninja-build \
        pkg-config \
        sqlite3 \
        tk-dev \
        zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*

# Flags: --enable-optimizations (PGO), --with-lto (Link-Time Optimization)
RUN git clone --depth 1 --branch $PYTHON_VER --single-branch https://github.com/python/cpython && \
    cd $HOME/cpython && \
    ./configure --enable-optimizations --with-lto --enable-loadable-sqlite-modules && \
    make -j $PARALLEL && \
    make install && \
    strip --strip-all /usr/local/bin/python* 2>/dev/null || true && \
    strip --strip-all /usr/local/lib/libpython*.so* 2>/dev/null || true && \
    cd / && \
    rm -rf $HOME/cpython $HOME/.cache

RUN pip3 install --no-cache-dir uv --root-user-action ignore && \
    strip --strip-all /usr/local/bin/uv 2>/dev/null || true

RUN ldconfig && \
    uv pip install --system --no-cache-dir certifi numpy setuptools && \
    uv pip install --system --no-cache-dir pyproj shapely --no-binary :all: && \
    python3 -c "import pyproj" && \
    python3 -c "import shapely"

# ============================================================================
# STAGE 2: build-gdal
# ============================================================================

FROM build-python AS build-gdal

ARG GDAL_VER
ARG PARALLEL

ENV HOME=/root \
    DEBIAN_FRONTEND=noninteractive
WORKDIR $HOME

RUN apt update && \
    apt install -y --no-install-recommends \
        cmake \
        curl \
        git \
        ninja-build \
        swig && \
    rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 --branch $GDAL_VER --single-branch https://github.com/OSGeo/gdal && \
    mkdir $HOME/gdal/build && \
    cd $HOME/gdal/build && \
    cmake -G Ninja \
        .. \
        -DCMAKE_BUILD_TYPE=Release \
        -DBUILD_PYTHON_BINDINGS=ON \
        -DPython_EXECUTABLE=/usr/local/bin/python3 \
        -DCMAKE_INTERPROCEDURAL_OPTIMIZATION=OFF \
        -DCMAKE_C_FLAGS_RELEASE="-g0" \
        -DCMAKE_CXX_FLAGS_RELEASE="-g0" && \
    ninja -j $PARALLEL install && \
    ldconfig && \
    find /usr/local/lib -name "libgdal*" -exec strip --strip-all {} \; 2>/dev/null || true && \
    find /usr/local/bin -name "gdal*" -exec strip --strip-all {} \; 2>/dev/null || true && \
    cd / && \
    rm -rf $HOME/gdal $HOME/.cache

RUN python3 -c "from osgeo import gdal"

# ============================================================================
# STAGE 3: build-arrow
# ============================================================================

FROM build-gdal AS build-arrow

ARG ARROW_VER
ARG PARALLEL

ENV HOME=/root \
    DEBIAN_FRONTEND=noninteractive \
    ARROW_DIR=$HOME/arrow \
    ARROW_HOME=/usr/local \
    CMAKE_PREFIX_PATH=/usr/local \
    PYARROW_PARALLEL=$PARALLEL \
    PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1

WORKDIR $HOME

RUN apt update && \
    apt install -y --no-install-recommends \
        cmake \
        curl \
        git \
        ninja-build \
        rustup && \
    rm -rf /var/lib/apt/lists/*

RUN ldconfig && rustup default stable

RUN echo "/usr/local/lib" >> /etc/ld.so.conf.d/99-local.conf && \
    echo "/usr/local/lib64" >> /etc/ld.so.conf.d/99-local.conf

RUN git clone --depth 1 --branch $ARROW_VER --single-branch https://github.com/apache/arrow && \
    mkdir -p $ARROW_DIR/cpp/build && \
    cd $ARROW_DIR/cpp/build && \
    uv pip install --system --no-cache-dir -r $ARROW_DIR/python/requirements-build.txt && \
    cmake -G Ninja -S $ARROW_DIR/cpp -B $ARROW_DIR/cpp/build \
        -DCMAKE_INSTALL_PREFIX=$ARROW_HOME \
        -DCMAKE_INSTALL_LIBDIR=lib \
        -DCMAKE_INTERPROCEDURAL_OPTIMIZATION=OFF \
        -DARROW_PARQUET=ON \
        -DARROW_COMPUTE=ON \
        -DARROW_DATASET=ON \
        -DARROW_IPC=ON \
        -DCMAKE_C_FLAGS_RELEASE="-g0" \
        -DCMAKE_CXX_FLAGS_RELEASE="-g0" \
        --preset ninja-release-python && \
    ninja -j $PARALLEL install && \
    ldconfig && \
    strip --strip-all /usr/local/lib/libarrow* 2>/dev/null || true && \
    cd $ARROW_DIR/python && \
    uv pip install --system --no-cache-dir . && \
    cd / && \
    rm -rf $HOME/arrow $HOME/.cache

RUN uv pip install --system --no-cache-dir geoarrow-pyarrow --no-binary :all: && \
    python3 -c "import pyarrow" && \
    python3 -c "import geoarrow.pyarrow"

# ============================================================================
# STAGE 4: install-gis
# ============================================================================

FROM build-arrow AS install-gis

# Install extra GIS packages, warn if not possible (next likely fails)
RUN uv pip install --system --no-cache-dir fiona geoalchemy2 geopandas geopy mapclassify psycopg psycopg2 --no-binary fiona || echo "WARNING: Extra packages did not build"
RUN uv cache clean

# ============================================================================
# STAGE 5: runtime
# ============================================================================

FROM install-gis AS runtime

# Python symlinks for convenience
RUN ln -sf /usr/local/bin/python3 /usr/bin/python && \
    ln -sf /usr/local/bin/pip3 /usr/local/bin/pip && \
    ln -sf /usr/local/bin/pip3 /usr/bin/pip
RUN python --version && pip --version

# Install Pixi package manager
RUN curl -fsSL https://pixi.sh/install.sh | sh
ENV PATH=$HOME/.pixi/bin:$PATH
RUN pixi self-update

# Pre-compile all Python modules to bytecode for faster first-import
# Then pin runtime dependencies
# Finally, purge build tools and strip symbols and remove build artifacts
RUN python3 -m py_compile $(find /usr/local/lib/python*/site-packages -name "*.py" -type f 2>/dev/null) 2>/dev/null || true && \
    apt-get install -y --no-install-recommends \
        libcurl4 \
        libexpat1 \
        libgeotiff5 \
        libpng16-16 \
        libpq5 \
        libssl3  \
        libtiff6 \
        && \
    apt-get purge -y \
        autoconf \
        automake \
        build-essential \
        cmake \
        libncurses-dev \
        libpq-dev \
        libreadline-dev \
        libssl-dev \
        libtool \
        libzstd-dev \
        lzma \
        ninja-build \
        pkg-config \
        python3-dev \
        rustup \
        swig \
        tk-dev \
        zlib1g-dev \
        && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    find /usr/local/lib/python*/site-packages -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true && \
    find /usr/local/lib/python*/site-packages -name "*.so" -exec strip --strip-unneeded {} \; 2>/dev/null || true && \
    find /usr/local/lib/python*/site-packages -name "*.so.debug" -delete 2>/dev/null || true && \
    find /usr/local/lib/python*/site-packages \( -name "conftest.py" -o -name "pytest.ini" -o -name "setup.cfg" \) -type f -delete 2>/dev/null || true && \
    find /usr/local/lib/python*/site-packages \( -name "*.c" -o -name "*.cpp" \) -type f -delete 2>/dev/null || true && \
    find /usr/local/lib -type d -name "cmake" -exec rm -rf {} + 2>/dev/null || true

# Verify all key libraries
RUN ldconfig && \
    python -c "import pyproj" && \
    python -c "import shapely" && \
    python -c "from osgeo import gdal" && \
    python -c "import pyarrow" && \
    python -c "import geoarrow.pyarrow"

CMD ["bash"]
