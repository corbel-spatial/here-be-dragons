# syntax=docker/dockerfile:1
FROM ghcr.io/corbel-spatial/here-be-dragons:base AS build-python

ARG PARALLEL
ARG PYTHON_VER

ENV HOME=/root
WORKDIR $HOME

RUN \
    git clone --depth 1 --branch $PYTHON_VER --single-branch https://github.com/python/cpython && \
    cd $HOME/cpython && \
    ./configure --enable-optimizations --with-lto && \
    make -j $PARALLEL && \
    make install && \
    rm -rd $HOME/cpython

RUN pip3 install uv --root-user-action ignore

RUN uv pip install --system certifi numpy setuptools
RUN uv pip install --system pyproj --no-binary :all:

FROM build-python AS build-gdal

ARG GDAL_VER
ARG PARALLEL

ENV HOME=/root
WORKDIR $HOME

RUN \
    git clone --depth 1 --branch $GDAL_VER --single-branch https://github.com/OSGeo/gdal && \
    mkdir $HOME/gdal/build && \
    cd $HOME/gdal/build && \
    cmake -G Ninja .. -DCMAKE_BUILD_TYPE=Release && \
    ninja -j $PARALLEL install && \
    ldconfig && \
    rm -rd $HOME/gdal
RUN python3 -c "from osgeo import gdal"

FROM build-gdal AS build-arrow

ARG ARROW_VER
ARG PARALLEL

ENV HOME=/root
WORKDIR $HOME

ENV ARROW_DIR=$HOME/arrow
ENV ARROW_HOME=$ARROW_DIR/dist
ENV LD_LIBRARY_PATH=$ARROW_DIR/dist/lib
ENV CMAKE_PREFIX_PATH=$ARROW_HOME
ENV PYARROW_PARALLEL=$PARALLEL
ENV PYARROW_BUNDLE_ARROW_CPP=1
ENV PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1
RUN \
    git clone --depth 1 --branch $ARROW_VER --single-branch https://github.com/apache/arrow && \
    mkdir $ARROW_HOME && \
    cd $ARROW_HOME && \
    uv pip install --system -r $ARROW_DIR/python/requirements-build.txt && \
    cmake -S $ARROW_DIR/cpp -B $ARROW_DIR/cpp/build \
        -DCMAKE_INSTALL_PREFIX=$ARROW_HOME \
        -DCMAKE_INSTALL_LIBDIR=lib \
        --preset ninja-release-python && \
    cmake --build $ARROW_DIR/cpp/build --target install --parallel $PARALLEL && \
    ldconfig && \
    cd $ARROW_DIR/python && \
    uv pip install --system . && \
    rm -rd $HOME/arrow

RUN uv pip install --system geoarrow-pyarrow --no-binary :all:
RUN python3 -c "import pyarrow"
RUN python3 -c "import geoarrow.pyarrow"

FROM build-arrow AS install-gis
RUN uv pip install --system fiona geoalchemy2 geopandas geopy mapclassify psycopg psycopg2 shapely || echo "WARNING: Extra packages did not build"

FROM install-gis AS runtime
RUN apt purge -y \
        build-essential  \
        ccache  \
        cmake  \
        gdb  \
        gfortran  \
        inetutils-inetd  \
        lcov  \
        libbz2-dev  \
        libcurl4-openssl-dev  \
        libcurlpp-dev  \
        libffi-dev \
        libgdbm-compat-dev \
        libgdbm-dev \
        libgeos-dev  \
        libgeotiff-dev \
        libgif-dev  \
        libjpeg-dev  \
        liblzma-dev  \
        libncurses-dev  \
        libopenblas-dev  \
        libpng-dev  \
        libpq-dev  \
        libproj-dev  \
        libreadline6-dev  \
        libsqlite3-dev \
        libssl-dev  \
        libtiff-dev  \
        libzstd-dev  \
        lzma  \
        ninja-build \
        pkg-config  \
        python3-dev  \
        rustup  \
        sqlite3 \
        swig \
        tk-dev  \
        uuid-dev  \
        zlib1g-dev && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*

RUN ln -sf /usr/local/bin/python3 /usr/bin/python && \
    ln -sf /usr/local/bin/pip3 /usr/local/bin/pip && \
    ln -sf /usr/local/bin/pip3 /usr/bin/pip

RUN ldconfig && \
    python -c "from osgeo import gdal" && \
    python -c "import pyarrow" && \
    python -c "import geoarrow.pyarrow"

RUN curl -fsSL https://pixi.sh/install.sh | sh
ENV PATH=$HOME/.pixi/bin:$PATH
RUN pixi self-update

CMD ["bash"]
