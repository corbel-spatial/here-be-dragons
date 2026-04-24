FROM ubuntu:rolling

ENV HOME=/root
WORKDIR $HOME

RUN \
   sed -i 's/^Types: deb$/Types: deb deb-src/' /etc/apt/sources.list.d/ubuntu.sources && \
   apt update && \
   apt upgrade -y && \
   apt build-dep python3 -y && \
   apt install -y --no-install-recommends \
       build-essential  \
       ca-certificates  \
       ccache  \
       cmake  \
       curl  \
       gdb  \
       gfortran  \
       git  \
       inetutils-inetd  \
       lcov \
       libbz2-dev  \
       libcurl4-openssl-dev  \
       libcurlpp-dev \
       libffi-dev \
       libgdbm-compat-dev  \
       libgdbm-dev  \
       libgeotiff-dev  \
       libgif-dev  \
       libjpeg-dev  \
       liblzma-dev \
       libncurses-dev \
       libopenblas-dev \
       libpng-dev  \
       libpq-dev  \
       libreadline6-dev  \
       libsqlite3-dev  \
       libssl-dev  \
       libtiff-dev  \
       libzstd-dev  \
       lzma  \
       ninja-build  \
       pkg-config  \
       python-is-python3  \
       python3-dev  \
       python3-pip  \
       python3-setuptools  \
       rustup  \
       sqlite3  \
       swig \
       tk-dev  \
       uuid-dev  \
       wget  \
       zlib1g-dev \
       && \
    rm -rf /var/lib/apt/lists/*

RUN rustup install stable

ARG PARALLEL

ARG GEOS_VER
RUN \
    git clone --depth 1 --branch $GEOS_VER --single-branch https://github.com/libgeos/geos && \
    mkdir geos/build && \
    cd geos/build && \
    cmake -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr/local ..  && \
    ninja -j $PARALLEL install && \
    rm -rd $HOME/geos

ARG PROJ_VER
RUN \
    git clone --depth 1 --branch $PROJ_VER --single-branch https://github.com/OSGeo/PROJ && \
    mkdir PROJ/build && \
    cd PROJ/build && \
    cmake -G Ninja .. && \
    ninja -j $PARALLEL install && \
    projsync --target-dir /var/cache/proj --all && \
    cp -a /var/cache/proj/. /usr/local/share/proj/ && \
    rm -rd $HOME/PROJ
