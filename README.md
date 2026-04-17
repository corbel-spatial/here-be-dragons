# 🌍 Here Be Dragons 🐲

A helpful Docker image for bleeding-edge spatial data analysis in Python.

Tricky dependencies are built from source so you can run the latest geoprocessing libraries that depend on Python, Arrow, GDAL, GEOS, and PROJ. 
See [`versions.toml`](versions.toml) for the list of packages built from source.

The Python package manager `uv` is pre-installed and is the recommended way to install additional packages.

## Getting Started

You will need to install [Docker](https://www.docker.com/get-started/). 

On Windows, running [Docker Desktop](https://docs.docker.com/desktop/features/wsl/) with 
[Windows Subsystem for Linux (WSL)](https://learn.microsoft.com/en-us/windows/wsl/install) is recommended.

## 🐍 Latest

This Docker image is the **stable** version intended for production work with common geospatial libraries in the latest version of Python. 
The image is built on top of the most recent Ubuntu Long-Term Support release (`ubuntu:latest`).

To pull and start the container in your terminal:

```shell
docker run -it --name here-be-dragons-latest ghcr.io/corbel-spatial/here-be-dragons:latest
```

After the image downloads and opens a terminal you can see which packages are already installed by running:

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

## 🔥 Next

This Docker image is the **experimental** version intended for testing the latest pre-release version of Python against Arrow, GDAL, GEOS, and PROJ. 
Failing builds might indicate that issues are on the horizon.
The image is built on top of the most recent Ubuntu release (`ubuntu:rolling`).

```shell
docker run -it --name here-be-dragons-next ghcr.io/corbel-spatial/here-be-dragons:next
```

## 📑 References 

| Project                                                                                           | Source                                                                         | Downstream Packages                                                                                     |
|:--------------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------|
| [Arrow](https://arrow.apache.org/)                                                                | https://github.com/apache/arrow                                                | [geoarrow-pyarrow](https://geoarrow.org/geoarrow-python/main/index.html)                                |
| [GDAL](https://gdal.org/)                                                                         | https://github.com/OSGeo/gdal                                                  | [Python bindings](https://pypi.org/project/GDAL/)                                                       |
| [GEOS](https://libgeos.org/)                                                                      | https://github.com/libgeos/geos                                                | [Shapely](https://shapely.readthedocs.io/)                                                              |
| [PROJ](https://proj.org/)                                                                         | https://github.com/OSGeo/PROJ                                                  | [Pyproj](https://pyproj4.github.io/pyproj/stable/)                                                      |
| [Python](https://www.python.org/)<br/>([release schedule](https://devguide.python.org/versions/)) | https://github.com/python/cpython                                              | [uv](https://docs.astral.sh/uv/), [Pixi](https://pixi.sh/latest/) |
| [Ubuntu](https://ubuntu.com/)                                                                     | https://hub.docker.com/_/ubuntu |                                                                                      n/a                   |
