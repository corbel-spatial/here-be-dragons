# syntax=docker/dockerfile:1
FROM ubuntu:rolling AS base-builder

# ============================================================================
# STAGE 1: Compile GEOS and PROJ geospatial libraries from source
# ============================================================================

ENV HOME=/root \
    DEBIAN_FRONTEND=noninteractive
WORKDIR $HOME

RUN apt update && \
    apt install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        cmake \
        curl \
        gfortran \
        git \
        libbz2-dev \
        libcurl4-openssl-dev \
        libcurlpp-dev \
        libffi-dev \
        libgdbm-compat-dev \
        libgdbm-dev \
        libgeotiff-dev \
        libgif-dev \
        libjpeg-dev \
        liblzma-dev \
        libncurses-dev \
        libopenblas-dev \
        libpng-dev \
        libpq-dev \
        libreadline6-dev \
        libsqlite3-dev \
        libssl-dev \
        libtiff-dev \
        libzstd-dev \
        lzma \
        ninja-build \
        pkg-config \
        python3-dev \
        python3-pip \
        python3-setuptools \
        sqlite3 \
        uuid-dev \
        wget \
        zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*

ARG PARALLEL

ARG GEOS_VER
RUN git clone --depth 1 --branch $GEOS_VER --single-branch https://github.com/libgeos/geos && \
    mkdir geos/build && \
    cd geos/build && \
    cmake -G Ninja \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INTERPROCEDURAL_OPTIMIZATION=ON \
        -DCMAKE_C_FLAGS_RELEASE="-g0" \
        -DCMAKE_CXX_FLAGS_RELEASE="-g0" \
        -DCMAKE_INSTALL_PREFIX=/usr/local \
        .. && \
    ninja -j $PARALLEL install && \
    cd / && \
    rm -rf $HOME/geos

ARG PROJ_VER
RUN git clone --depth 1 --branch $PROJ_VER --single-branch https://github.com/OSGeo/PROJ && \
    mkdir PROJ/build && \
    cd PROJ/build && \
    cmake -G Ninja \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INTERPROCEDURAL_OPTIMIZATION=ON \
        -DCMAKE_C_FLAGS_RELEASE="-g0" \
        -DCMAKE_CXX_FLAGS_RELEASE="-g0" \
        .. && \
    ninja -j $PARALLEL install && \
    projsync --target-dir /var/cache/proj --all && \
    cp -a /var/cache/proj/. /usr/local/share/proj/ && \
    cd / && \
    rm -rf /var/cache/proj $HOME/PROJ $HOME/.cache/pip

RUN strip --strip-all /usr/local/lib/*.so* /usr/local/lib/lib*.a 2>/dev/null || true && \
    strip --strip-all /usr/local/bin/* 2>/dev/null || true && \
    find /usr/local/lib -name "*.a" -delete

# ============================================================================
# STAGE 2: base-runtime
# ============================================================================

FROM ubuntu:rolling AS base-runtime

ENV HOME=/root \
    DEBIAN_FRONTEND=noninteractive
WORKDIR $HOME

# Install runtime dependencies only (no build tools)
RUN apt update && \
    apt install -y --no-install-recommends \
        ca-certificates \
        libcurl4 \
        libgdbm6 \
        libgeotiff5 \
        libgif7 \
        libjpeg-turbo8 \
        libopenblas0 \
        libpng16-16 \
        libpq5 \
        libsqlite3-0 \
        libssl3 \
        libtiff6 \
        libzstd1 \
        lzma \
        sqlite3 \
        uuid-runtime \
        wget && \
    rm -rf /var/lib/apt/lists/*

COPY --from=base-builder /usr/local/lib /usr/local/lib
COPY --from=base-builder /usr/local/bin /usr/local/bin
COPY --from=base-builder /usr/local/share/proj /usr/local/share/proj
COPY --from=base-builder /usr/local/include /usr/local/include

RUN strip --strip-all /usr/local/lib/*.so* /usr/local/bin/* 2>/dev/null || true && \
    strip --strip-unneeded /usr/local/lib/*.so* /usr/local/bin/* 2>/dev/null || true && \
    ldconfig && \
    geos-config --version && \
    projinfo 2>&1 | head -n 1

CMD ["bash"]
