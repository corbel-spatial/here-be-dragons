# 🌍 Here Be Dragons 🐲

A helpful Docker image for bleeding-edge spatial data analysis in Python.

Tricky dependencies are built from source so you can run the latest geoprocessing libraries that depend on Python, Arrow, GDAL, GEOS, and PROJ.

The Python package manager `uv` is pre-installed and is the recommended way to install additional packages.

> [!TIP]
> You will need to install [Docker](https://www.docker.com/get-started/). On Windows, running [Docker Desktop](https://docs.docker.com/desktop/features/wsl/) with [Windows Subsystem for Linux (WSL)](https://learn.microsoft.com/en-us/windows/wsl/install) is recommended.


## 🐍 Latest
[![Latest Python Version](https://img.shields.io/badge/dynamic/regex?url=https%3A%2F%2Fraw.githubusercontent.com%2Fcorbel-spatial%2Fhere-be-dragons%2Frefs%2Fheads%2Fmain%2Fversions.env&search=(PYTHON_VER_LATEST%3D)(.*)&replace=%242&logo=python&logoColor=yellow&label=python&labelColor=steelblue&color=steelblue)](#)
[![Latest Arrow Version](https://img.shields.io/badge/dynamic/regex?url=https%3A%2F%2Fraw.githubusercontent.com%2Fcorbel-spatial%2Fhere-be-dragons%2Frefs%2Fheads%2Fmain%2Fversions.env&search=(ARROW_VER_LATEST%3D)(.*)&replace=%242&logo=apache&logoColor=orange&label=%20&labelColor=mediumpurple&color=mediumpurple)](#)
[![Latest GDAL Version](https://img.shields.io/badge/dynamic/regex?url=https%3A%2F%2Fraw.githubusercontent.com%2Fcorbel-spatial%2Fhere-be-dragons%2Frefs%2Fheads%2Fmain%2Fversions.env&search=(GDAL_VER_LATEST%3D)(.*)&replace=%242&logo=gdal&logoColor=darkgreen&label=GDAL&labelColor=mediumseagreen&color=mediumseagreen)](#)
[![GEOS Version](https://img.shields.io/badge/dynamic/regex?url=https%3A%2F%2Fraw.githubusercontent.com%2Fcorbel-spatial%2Fhere-be-dragons%2Frefs%2Fheads%2Fmain%2Fversions.env&search=(GEOS_VER%3D)(.*)&replace=%242&logo=osgeo&logoColor=green&label=GEOS&labelColor=slategray&color=slategray)](#)
[![PROJ Version](https://img.shields.io/badge/dynamic/regex?url=https%3A%2F%2Fraw.githubusercontent.com%2Fcorbel-spatial%2Fhere-be-dragons%2Frefs%2Fheads%2Fmain%2Fversions.env&search=(PROJ_VER%3D)(.*)&replace=%242&logo=osgeo&logoColor=green&label=PROJ&labelColor=slategray&color=slategray)](#)

[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/corbel-spatial/here-be-dragons/build-latest.yml?branch=main)](https://github.com/corbel-spatial/here-be-dragons/actions/workflows/build-latest.yml?query=branch%3Amain)
[![Ubuntu Version](https://img.shields.io/docker/v/_/ubuntu/rolling?logo=ubuntu&logoColor=white&label=ubuntu&labelColor=tomato&color=tomato)](#)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](#)
[![Pixi Badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/prefix-dev/pixi/main/assets/badge/v0.json)](https://pixi.sh)

![GitHub Actions Workflow Status - Latest amd64](https://img.shields.io/github/actions/workflow/status/corbel-spatial/here-be-dragons/build-latest-amd64.yml?style=flat-square&label=amd64)
![GitHub Actions Workflow Status - Latest arm64](https://img.shields.io/github/actions/workflow/status/corbel-spatial/here-be-dragons/build-latest-arm64.yml?style=flat-square&label=arm64)
![Arrow Version](https://img.shields.io/badge/dynamic/toml?url=https%3A%2F%2Fraw.githubusercontent.com%2Fcorbel-spatial%2Fhere-be-dragons%2Frefs%2Fheads%2Fmain%2Fversions.toml&query=%24.latest.ARROW&style=flat-square&logo=apache&logoColor=purple&label=arrow)
![GDAL Version](https://img.shields.io/badge/dynamic/toml?url=https%3A%2F%2Fraw.githubusercontent.com%2Fcorbel-spatial%2Fhere-be-dragons%2Frefs%2Fheads%2Fmain%2Fversions.toml&query=%24.latest.GDAL&style=flat-square&logo=gdal&logoColor=green&label=gdal)
![GEOS Version](https://img.shields.io/badge/dynamic/toml?url=https%3A%2F%2Fraw.githubusercontent.com%2Fcorbel-spatial%2Fhere-be-dragons%2Frefs%2Fheads%2Fmain%2Fversions.toml&query=%24.latest.GEOS&style=flat-square&logo=osgeo&logoColor=green&label=geos)
![PROJ Version](https://img.shields.io/badge/dynamic/toml?url=https%3A%2F%2Fraw.githubusercontent.com%2Fcorbel-spatial%2Fhere-be-dragons%2Frefs%2Fheads%2Fmain%2Fversions.toml&query=%24.latest.PROJ&style=flat-square&logo=osgeo&logoColor=green&label=proj)
![Python Version](https://img.shields.io/badge/dynamic/toml?url=https%3A%2F%2Fraw.githubusercontent.com%2Fcorbel-spatial%2Fhere-be-dragons%2Frefs%2Fheads%2Fmain%2Fversions.toml&query=%24.latest.PYTHON&style=flat-square&logo=python&logoColor=yellow&label=python)

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
[![Next Python Version](https://img.shields.io/badge/dynamic/regex?url=https%3A%2F%2Fraw.githubusercontent.com%2Fcorbel-spatial%2Fhere-be-dragons%2Frefs%2Fheads%2Fmain%2Fversions.env&search=(PYTHON_VER_NEXT%3D)(.*)&replace=%242&logo=python&logoColor=yellow&label=python&labelColor=steelblue&color=steelblue)](#)
[![Next Arrow Version](https://img.shields.io/badge/dynamic/regex?url=https%3A%2F%2Fraw.githubusercontent.com%2Fcorbel-spatial%2Fhere-be-dragons%2Frefs%2Fheads%2Fmain%2Fversions.env&search=(ARROW_VER_NEXT%3D)(.*)&replace=%242&logo=apache&logoColor=orange&label=%20&labelColor=mediumpurple&color=mediumpurple)](#)
[![Next GDAL Version](https://img.shields.io/badge/dynamic/regex?url=https%3A%2F%2Fraw.githubusercontent.com%2Fcorbel-spatial%2Fhere-be-dragons%2Frefs%2Fheads%2Fmain%2Fversions.env&search=(GDAL_VER_NEXT%3D)(.*)&replace=%242&logo=gdal&logoColor=darkgreen&label=GDAL&labelColor=mediumseagreen&color=mediumseagreen)](#)
[![GEOS Version](https://img.shields.io/badge/dynamic/regex?url=https%3A%2F%2Fraw.githubusercontent.com%2Fcorbel-spatial%2Fhere-be-dragons%2Frefs%2Fheads%2Fmain%2Fversions.env&search=(GEOS_VER%3D)(.*)&replace=%242&logo=osgeo&logoColor=green&label=GEOS&labelColor=slategray&color=slategray)](#)
[![PROJ Version](https://img.shields.io/badge/dynamic/regex?url=https%3A%2F%2Fraw.githubusercontent.com%2Fcorbel-spatial%2Fhere-be-dragons%2Frefs%2Fheads%2Fmain%2Fversions.env&search=(PROJ_VER%3D)(.*)&replace=%242&logo=osgeo&logoColor=green&label=PROJ&labelColor=slategray&color=slategray)](#)

[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/corbel-spatial/here-be-dragons/build-next.yml?branch=main)](https://github.com/corbel-spatial/here-be-dragons/actions/workflows/build-next.yml?query=branch%3Amain)
[![Ubuntu Version](https://img.shields.io/docker/v/_/ubuntu/rolling?logo=ubuntu&logoColor=white&label=ubuntu&labelColor=tomato&color=tomato)](#)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](#)
[![Pixi Badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/prefix-dev/pixi/main/assets/badge/v0.json)](https://pixi.sh)

![GitHub Actions Workflow Status - Next amd64](https://img.shields.io/github/actions/workflow/status/corbel-spatial/here-be-dragons/build-next-amd64.yml?style=flat-square&label=amd64)
![GitHub Actions Workflow Status - Next arm64](https://img.shields.io/github/actions/workflow/status/corbel-spatial/here-be-dragons/build-next-arm64.yml?style=flat-square&label=arm64)
![Arrow Version](https://img.shields.io/badge/dynamic/toml?url=https%3A%2F%2Fraw.githubusercontent.com%2Fcorbel-spatial%2Fhere-be-dragons%2Frefs%2Fheads%2Fmain%2Fversions.toml&query=%24.next.ARROW&style=flat-square&logo=apache&logoColor=purple&label=arrow)
![GDAL Version](https://img.shields.io/badge/dynamic/toml?url=https%3A%2F%2Fraw.githubusercontent.com%2Fcorbel-spatial%2Fhere-be-dragons%2Frefs%2Fheads%2Fmain%2Fversions.toml&query=%24.next.GDAL&style=flat-square&logo=gdal&logoColor=green&label=gdal)
![GEOS Version](https://img.shields.io/badge/dynamic/toml?url=https%3A%2F%2Fraw.githubusercontent.com%2Fcorbel-spatial%2Fhere-be-dragons%2Frefs%2Fheads%2Fmain%2Fversions.toml&query=%24.next.GEOS&style=flat-square&logo=osgeo&logoColor=green&label=geos)
![PROJ Version](https://img.shields.io/badge/dynamic/toml?url=https%3A%2F%2Fraw.githubusercontent.com%2Fcorbel-spatial%2Fhere-be-dragons%2Frefs%2Fheads%2Fmain%2Fversions.toml&query=%24.next.PROJ&style=flat-square&logo=osgeo&logoColor=green&label=proj)
![Python Version](https://img.shields.io/badge/dynamic/toml?url=https%3A%2F%2Fraw.githubusercontent.com%2Fcorbel-spatial%2Fhere-be-dragons%2Frefs%2Fheads%2Fmain%2Fversions.toml&query=%24.next.PYTHON&style=flat-square&logo=python&logoColor=yellow&label=python)

This Docker image is the **experimental** version intended for testing the latest pre-release version of Python against Arrow, GDAL, GEOS, and PROJ. 
Failing builds might indicate that issues are on the horizon.
The image is built on top of the most recent Ubuntu release (`ubuntu:rolling`).

```shell
docker run -it --name here-be-dragons-next ghcr.io/corbel-spatial/here-be-dragons:next
```

## ⚠️ TODO

- Scheduled automatic update of `versions.env` to find new releases/tags
- Reduce the size of the images (< 3gb?)
- Add `latest-dev` and `next-dev` tags that keep all the build dependencies
- Images should run as non-root user
- Create a benchmark suite and check new releases for performance regressions
- Add more packages upon request - please open an issue!

## 📚 References 

| Project                                                                                           | Source                            | Downstream Packages                                                      |
|:--------------------------------------------------------------------------------------------------|:----------------------------------|:-------------------------------------------------------------------------|
| [Arrow](https://arrow.apache.org/)                                                                | https://github.com/apache/arrow   | [geoarrow-pyarrow](https://geoarrow.org/geoarrow-python/main/index.html) |
| [GDAL](https://gdal.org/)                                                                         | https://github.com/OSGeo/gdal     | [Python bindings](https://pypi.org/project/GDAL/)                        |
| [GEOS](https://libgeos.org/)                                                                      | https://github.com/libgeos/geos   | [Shapely](https://shapely.readthedocs.io/)                               |
| [PROJ](https://proj.org/)                                                                         | https://github.com/OSGeo/PROJ     | [Pyproj](https://pyproj4.github.io/pyproj/stable/)                       |
| [Python](https://www.python.org/)<br/>([release schedule](https://devguide.python.org/versions/)) | https://github.com/python/cpython | [uv](https://docs.astral.sh/uv/), [Pixi](https://pixi.sh/latest/)        |
| [Ubuntu](https://ubuntu.com/)                                                                     | https://hub.docker.com/_/ubuntu   | n/a                                                                      |
