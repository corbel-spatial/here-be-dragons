# syntax=docker/dockerfile:1
FROM ubuntu:latest AS builder

LABEL org.opencontainers.image.base.name=docker.io/ubuntu:latest
LABEL org.opencontainers.image.source=https://github.com/corbel-spatial/here-be-dragons
LABEL org.opencontainers.image.documentation=https://here-be-dragons.readthedocs.io/
LABEL org.opencontainers.image.title="here-be-dragons:latest"
LABEL org.opencontainers.image.description="Docker image for bleeding-edge spatial data analysis in Python"
LABEL org.opencontainers.image.licenses=MIT
LABEL org.opencontainers.image.authors="dev@corbelspatial.com"

# Build system dependencies
FROM builder AS build-sysdeps
ARG PARALLEL
ENV HOME=/root
ENV BUILDS=$HOME/builds
WORKDIR $BUILDS
RUN \
    sed -i 's/^Types: deb$/Types: deb deb-src/' /etc/apt/sources.list.d/ubuntu.sources && \
    apt update && \
    apt upgrade -y && \
    apt build-dep python3 -y && \
    apt install -y --no-install-recommends \
        build-essential ca-certificates cmake curl git gdb inetutils-inetd lcov \
        libbz2-dev libcurl4-openssl-dev libcurlpp-dev libjpeg-dev libffi-dev libgdbm-dev libgdbm-compat-dev libgeos-dev libgeotiff-dev libgif-dev \
        liblzma-dev libncurses5-dev libpng-dev libpq-dev libproj-dev libreadline6-dev libsqlite3-dev libssl-dev libtiff5-dev libzstd-dev \
        lzma lzma-dev ninja-build pkg-config python-is-python3 python3-dev sqlite3 tk-dev uuid-dev wget zlib1g-dev && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*

# Build Python
# https://devguide.python.org/getting-started/setup-building/#build-dependencies
FROM build-sysdeps AS build-python
ARG PYTHON_VER
#RUN \
#    sed -i 's/^Types: deb$/Types: deb deb-src/' /etc/apt/sources.list.d/ubuntu.sources && \
#    apt update && \
#    apt build-dep python3 -y && \
#    apt install -y --no-install-recommends \
#          ca-certificates git \
#          pkg-config build-essential gdb lcov pkg-config \
#          libbz2-dev libffi-dev libgdbm-dev libgdbm-compat-dev liblzma-dev \
#          libncurses5-dev libreadline6-dev libsqlite3-dev libssl-dev \
#          lzma lzma-dev tk-dev uuid-dev zlib1g-dev libzstd-dev inetutils-inetd
RUN git clone --depth 1 --branch $PYTHON_VER --single-branch https://github.com/python/cpython
RUN \
    cd $BUILDS/cpython && \
    ./configure --enable-optimizations --with-lto && \
    make -j $PARALLEL && \
    make test -j $PARALLEL && \
    make install && \
    pip3 install uv --root-user-action ignore && \
    cd $BUILDS && \
    rm -rd $BUILDS/cpython

## Build GEOS
## https://libgeos.org/usage/download/
FROM build-python AS build-geos
ARG GEOS_VER
#RUN apt update && apt install -y --no-install-recommends \
#    ca-certificates git build-essential cmake
RUN git clone --depth 1 --branch $GEOS_VER --single-branch https://github.com/libgeos/geos
RUN \
    mkdir $BUILDS/geos/build && \
    cd $BUILDS/geos/build && \
    cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr/local ..  && \
    make -j $PARALLEL && \
    ctest --parallel $PARALLEL && \
    make install && \
    cd $BUILDS && \
    rm -rd $BUILDS/geos
RUN \
    uv pip install --system \
        numpy shapely --no-binary :all:

## Build PROJ
## https://proj.org/en/stable/install.html
FROM build-geos AS build-proj
ARG PROJ_VER
#RUN apt update && apt install -y --no-install-recommends \
#    ca-certificates git build-essential cmake sqlite3 libtiff5-dev libcurlpp-dev
RUN git clone --depth 1 --branch $PROJ_VER --single-branch https://github.com/OSGeo/PROJ
RUN \
    mkdir $BUILDS/PROJ/build && \
    cd $BUILDS/PROJ/build && \
    cmake .. && \
    cmake --build . --parallel $PARALLEL && \
    cmake --build . --target install --parallel $PARALLEL && \
    ctest ctest --parallel $PARALLEL && \
    projsync --system-directory --all && \
    cd $BUILDS && \
    rm -rd $BUILDS/PROJ
RUN \
    uv pip install --system \
        pyproj --no-binary :all:

## Build GDAL
## https://gdal.org/en/stable/development/building_from_source.html
## https://gist.github.com/samapriya/412babdfd3530c2766acb9d603ed1bb9
FROM build-proj AS build-gdal
ARG GDAL_VER
RUN git clone --depth 1 --branch $GDAL_VER --single-branch https://github.com/OSGeo/gdal
#RUN apt update && apt install -y --no-install-recommends \
#    ca-certificates git cmake build-essential libproj-dev libgeos-dev libsqlite3-dev libcurl4-openssl-dev \
#    libtiff5-dev libgeotiff-dev libpng-dev libjpeg-dev libgif-dev
RUN \
    mkdir $BUILDS/gdal/build && \
    cd $BUILDS/gdal/build && \
    cmake .. -DCMAKE_BUILD_TYPE=Release && \
    make -j $PARALLEL && \
    make install && \
    ldconfig && \
    uv pip install --system gdal==$GDAL_VER --no-binary :all: && \
    cd $BUILDS && \
    rm -rd $BUILDS/gdal && \
    python3 -c "from osgeo import gdal; print(gdal.__version__)"

## Build Arrow
## https://arrow.apache.org/docs/developers/python.html#building-on-linux-and-macos
FROM build-gdal AS build-arrow
ARG ARROW_VER
ENV ARROW_DIR=$BUILDS/arrow
ENV PARQUET_TEST_DATA=$ARROW_DIR/cpp/submodules/parquet-testing/data
ENV ARROW_TEST_DATA=$ARROW_DIR/testing/data
ENV ARROW_HOME=$ARROW_DIR/dist
ENV LD_LIBRARY_PATH=$ARROW_DIR/dist/lib
ENV CMAKE_PREFIX_PATH=$ARROW_HOME
ENV PYARROW_PARALLEL=$PARALLEL
ENV PYARROW_BUNDLE_ARROW_CPP=1
#RUN apt update && apt install -y --no-install-recommends \
#    git ca-certificates cmake build-essential ninja-build python3-dev
RUN git clone --depth 1 --branch $ARROW_VER --single-branch https://github.com/apache/arrow
RUN mkdir $ARROW_HOME && \
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
    cd $BUILDS && \
    python3 -c "import pyarrow; print(pyarrow.__version__)" && \
    rm -rd $BUILDS/arrow
RUN \
    uv pip install --system \
        geoarrow-pyarrow --no-binary :all:

FROM build-arrow AS install-pixi
#RUN apt update && apt install -y --no-install-recommends \
#    curl
RUN curl -fsSL https://pixi.sh/install.sh | sh
ENV PATH=$HOME/.pixi/bin:$PATH

FROM install-pixi AS install-gis
#RUN apt update && apt install -y --no-install-recommends \
#    libpq-dev
RUN \
    uv pip install --system \
        fiona \
        geoalchemy2 \
        geopandas \
        geopy \
        matplotlib \
        mapclassify \
        psycopg \
        psycopg2

FROM install-gis AS cleanup
WORKDIR $HOME
RUN \
    rm -rd $BUILDS && \
    rm /usr/bin/python && \
    ln -s /usr/local/bin/python3 /usr/bin/python && \
    ln -s /usr/local/bin/pip3 /usr/local/bin/pip && \
    ln -s /usr/local/bin/pip3 /usr/bin/pip

