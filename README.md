# Here Be Dragons 🌍 🐲

A helpful Docker image for bleeding-edge spatial data analysis in Python.

We build the low-level C binaries from source so you don't have to. 
These images are built on top of Ubuntu Linux and the most recent versions of 
Python, Arrow, GDAL, GEOS, and PROJ.

The Python package manager `uv` is pre-installed and the recommended way to 
install additional packages. `git`, `pip`, and `Pixi` are also included.

## Getting Started

You will need to [install Docker](https://www.docker.com/get-started/). 

On Windows, we recommend using [Docker Desktop and Windows Subsystem for Linux (WSL)](https://docs.docker.com/desktop/features/wsl/).

## Latest 🐍 Python 3.14.0

This is the **stable** version intended for production work. 

To pull and start the container in your terminal:

```shell
docker run -it --name here-be-dragons-latest ghcr.io/corbel-spatial/here-be-dragons:latest
```

After the image downloads and opens a terminal you can check which packages are already installed by running:

```shell
uv pip list
```

`geopandas` and common dependencies are pre-installed, which you can check with:

```shell
python -c "import geopandas; geopandas.show_versions()"
```

To install additional packages use `uv pip install --system`, for example:
```shell
uv pip install --system geojson duckdb sedonadb
```

To update and restart the stopped container:

```shell
docker pull ghcr.io/corbel-spatial/here-be-dragons:latest
docker start here-be-dragons-latest
docker attach here-be-dragons-latest
```

These are the current included versions of the binaries and the packages built with them:

| Binary Source  |               Python Packages               |
|:--------------:|:-------------------------------------------:|
| Arrow (21.0.0) | pyarrow (21.0.0)<br/>geoarrow-pyarrow (0.2) |
| GDAL (3.11.4)  |                gdal (3.11.4)                |
| GEOS (3.14.0)  |               shapely (2.1.2)               |
|  PROJ (9.7.0)  |      gdal (3.11.4)<br/>pyproj (3.7.2)       |

## Next 🔥 Python 3.15.0a1

This is the **experimental** version intended for testing Arrow, GDAL, GEOS, and PROJ
against the latest pre-release version of Python, and with and other packages in development.

The extra Python packages (`geopandas`, etc.) are not included.
Unstable source branches will be used if they are needed for a successful build.

```shell
docker run -it --name here-be-dragons-next ghcr.io/corbel-spatial/here-be-dragons:next
```

:warning: Note: Arrow cannot yet build successfully on Python 3.15 so it is not included :warning:

| Binary Source |         Python Packages          |
|:-------------:|:--------------------------------:|
|     Arrow     |                🚧                |
| GDAL (3.11.4) |          gdal (3.11.4)           |
| GEOS (3.14.0) |         shapely (2.1.2)          |
| PROJ (9.7.0)  | gdal (3.11.4)<br/>pyproj (3.7.2) |

## 📑 References 

| Project                                                                                           | Source                                                                         | Downstream Packages                                                                                     |
|:--------------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------|
| [Arrow](https://arrow.apache.org/)                                                                | https://github.com/apache/arrow                                                | [geoarrow-pyarrow](https://geoarrow.org/geoarrow-python/main/index.html)                                |
| [GDAL](https://gdal.org/)                                                                         | https://github.com/OSGeo/gdal                                                  | [Python bindings](https://pypi.org/project/GDAL/)                                                       |
| [GEOS](https://libgeos.org/)                                                                      | https://github.com/libgeos/geos                                                | [Shapely](https://shapely.readthedocs.io/)                                                              |
| [PROJ](https://proj.org/)                                                                         | https://github.com/OSGeo/PROJ                                                  | [Pyproj](https://pyproj4.github.io/pyproj/stable/)                                                      |
| [Python](https://www.python.org/)<br/>([release schedule](https://devguide.python.org/versions/)) | https://github.com/python/cpython                                              | [uv](https://docs.astral.sh/uv/), [Pixi](https://pixi.sh/latest/), [pip](https://pypi.org/project/pip/) |
| [Ubuntu](https://ubuntu.com/)                                                                     | Docker image [ubuntu:latest](https://hub.docker.com/_/ubuntu/tags?name=latest) |                                                                                                         |