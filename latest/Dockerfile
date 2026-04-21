# syntax=docker/dockerfile:1
FROM ubuntu:latest AS builder

LABEL org.opencontainers.image.base.name=docker.io/ubuntu:latest
LABEL org.opencontainers.image.source=https://github.com/corbel-spatial/here-be-dragons
LABEL org.opencontainers.image.documentation=https://here-be-dragons.readthedocs.io/
LABEL org.opencontainers.image.title="here-be-dragons:latest"
LABEL org.opencontainers.image.description="Docker image for bleeding-edge spatial data analysis in Python"
LABEL org.opencontainers.image.licenses=MIT
LABEL org.opencontainers.image.authors="dev@corbelspatial.com"

FROM builder AS build-sysdeps
ARG PARALLEL
ARG TARGETARCH
ENV HOME=/root
ENV BUILDS=$HOME/builds
WORKDIR $BUILDS

# Configure APT to keep downloaded packages for BuildKit caching
RUN rm -f /etc/apt/apt.conf.d/docker-clean; echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache

# Mount APT caches to drastically speed up system dependency installation on rebuilds
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    sed -i 's/^Types: deb$/Types: deb deb-src/' /etc/apt/sources.list.d/ubuntu.sources && \
    apt update && \
    apt upgrade -y && \
    apt build-dep python3 -y && \
    apt install -y --no-install-recommends \
        build-essential ca-certificates ccache cmake curl git gdb inetutils-inetd lcov \
        libbz2-dev libcurl4-openssl-dev libcurlpp-dev \
        libjpeg-dev libffi-dev libgdbm-dev libgdbm-compat-dev libgeos-dev libgeotiff-dev libgif-dev \
        liblzma-dev libncurses-dev libpng-dev libpq-dev libproj-dev libreadline6-dev libsqlite3-dev libssl-dev libtiff-dev libzstd-dev \
        lzma lzma-dev ninja-build pkg-config python-is-python3 python3-dev sqlite3 swig tk-dev uuid-dev wget zlib1g-dev \
        && \
    apt clean

ENV PATH="/usr/lib/ccache:$PATH"

# Build Python
FROM build-sysdeps AS build-python
ARG PYTHON_VER
ARG PARALLEL
ARG TARGETARCH
RUN --mount=type=cache,target=/root/.ccache-${TARGETARCH} \
    export CCACHE_DIR=/root/.ccache-${TARGETARCH} && \
    git clone --depth 1 --branch $PYTHON_VER --single-branch https://github.com/python/cpython && \
    cd $BUILDS/cpython && \
    ./configure --enable-optimizations --with-lto && \
    make -j $PARALLEL && \
    make install && \
    pip3 install uv --root-user-action ignore && \
    cd $BUILDS && \
    rm -rd $BUILDS/cpython

# Build GEOS
FROM build-python AS build-geos
ARG GEOS_VER
ARG PARALLEL
ARG TARGETARCH
RUN --mount=type=cache,target=/root/.ccache-${TARGETARCH} \
    export CCACHE_DIR=/root/.ccache-${TARGETARCH} && \
    git clone --depth 1 --branch $GEOS_VER --single-branch https://github.com/libgeos/geos && \
    mkdir $BUILDS/geos/build && \
    cd $BUILDS/geos/build && \
    cmake -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr/local ..  && \
    ninja -j $PARALLEL install && \
    cd $BUILDS && \
    rm -rd $BUILDS/geos
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system numpy shapely --no-binary :all:

# Build PROJ
FROM build-geos AS build-proj
ARG PROJ_VER
ARG PARALLEL
ARG TARGETARCH
RUN --mount=type=cache,target=/root/.ccache-${TARGETARCH} \
    --mount=type=cache,target=/var/cache/proj \
    export CCACHE_DIR=/root/.ccache-${TARGETARCH} && \
    git clone --depth 1 --branch $PROJ_VER --single-branch https://github.com/OSGeo/PROJ && \
    mkdir $BUILDS/PROJ/build && \
    cd $BUILDS/PROJ/build && \
    cmake -G Ninja .. && \
    ninja -j $PARALLEL install && \
    projsync --target-dir /var/cache/proj --all && \
    cp -a /var/cache/proj/. /usr/local/share/proj/ && \
    cd $BUILDS && \
    rm -rd $BUILDS/PROJ
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system pyproj --no-binary :all:

# Build GDAL
FROM build-proj AS build-gdal
ARG GDAL_VER
ARG PARALLEL
ARG TARGETARCH
RUN --mount=type=cache,target=/root/.ccache-${TARGETARCH} \
    --mount=type=cache,target=/root/.cache/uv \
    export CCACHE_DIR=/root/.ccache-${TARGETARCH} && \
    git clone --depth 1 --branch $GDAL_VER --single-branch https://github.com/OSGeo/gdal && \
    mkdir $BUILDS/gdal/build && \
    cd $BUILDS/gdal/build && \
    cmake -G Ninja .. -DCMAKE_BUILD_TYPE=Release && \
    ninja -j $PARALLEL install && \
    ldconfig && \
    cd $BUILDS/gdal/build/swig/python && \
    uv pip install --system . && \
    cd $BUILDS && \
    rm -rd $BUILDS/gdal

# Build Arrow
FROM build-gdal AS build-arrow
ARG ARROW_VER
ARG PARALLEL
ARG TARGETARCH
ENV ARROW_DIR=$BUILDS/arrow
ENV ARROW_HOME=$ARROW_DIR/dist
ENV LD_LIBRARY_PATH=$ARROW_DIR/dist/lib
ENV CMAKE_PREFIX_PATH=$ARROW_HOME
ENV PYARROW_PARALLEL=$PARALLEL
ENV PYARROW_BUNDLE_ARROW_CPP=1
RUN --mount=type=cache,target=/root/.ccache-${TARGETARCH} \
    --mount=type=cache,target=/root/.cache/uv \
    export CCACHE_DIR=/root/.ccache-${TARGETARCH} && \
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
    cd $BUILDS && \
    rm -rd $BUILDS/arrow
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system geoarrow-pyarrow --no-binary :all:

# Install Python GIS Tools
FROM build-arrow AS install-gis
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system fiona geoalchemy2 geopandas geopy matplotlib mapclassify psycopg psycopg2

# Create runtime environment
FROM ubuntu:latest AS runtime

# Install strictly runtime shared libraries (no -dev or build-essential packages)
RUN apt update && \
    apt install -y --no-install-recommends \
        ca-certificates curl \
        libbz2-1.0 libcurl4 libjpeg8 libffi8 libgdbm6 \
        liblzma5 libncurses6 libpng16-16 libpq5 libreadline8 \
        libsqlite3-0 libssl3 libtiff6 libzstd1 \
        lzma sqlite3 zlib1g && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*

# Copy compiled Python, GDAL, GEOS, PROJ, and Py-Packages from the builder stage
COPY --from=install-gis /usr/local /usr/local

# Update shared library cache and symlink Python
RUN ldconfig && \
    ln -s /usr/local/bin/python3 /usr/bin/python && \
    ln -s /usr/local/bin/pip3 /usr/local/bin/pip && \
    ln -s /usr/local/bin/pip3 /usr/bin/pip

# Create a non-root user for security
RUN useradd -m -s /bin/bash gis && \
    chown -R gis:gis /usr/local

USER gis
ENV HOME=/home/gis
WORKDIR $HOME

# Install Pixi as the unprivileged user
RUN curl -fsSL https://pixi.sh/install.sh | sh
ENV PATH=$HOME/.pixi/bin:$PATH

CMD ["bash"]