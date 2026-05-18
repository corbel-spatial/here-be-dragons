# 🌍 Here Be Dragons 🐲

A helpful Docker image for bleeding-edge spatial data analysis in Python.

Tricky dependencies are built from source so you can run the latest Python geoprocessing libraries that depend on Arrow, GDAL, GEOS, and PROJ.

The images are built on top of the most recent Ubuntu release (`ubuntu:rolling`) with [optimized](https://github.com/python/cpython#profile-guided-optimization) Python builds.
The Python package managers `uv` and `Pixi` come pre-installed.

By default, running the Docker images launches a [marimo](https://marimo.io/) notebook.

> [!TIP]
> You will need to install [Docker](https://www.docker.com/get-started/). On Windows, running [Docker Desktop](https://docs.docker.com/desktop/features/wsl/) with [Windows Subsystem for Linux (WSL)](https://learn.microsoft.com/en-us/windows/wsl/install) is recommended.


## 🐍 Latest
[![Latest Python Version](https://img.shields.io/badge/dynamic/regex?url=https%3A%2F%2Fraw.githubusercontent.com%2Fcorbel-spatial%2Fhere-be-dragons%2Frefs%2Fheads%2Fmain%2Fversions.env&search=(PYTHON_VER_LATEST%3D)(.*)&replace=%242&logo=python&logoColor=yellow&label=python&labelColor=steelblue&color=steelblue)](https://github.com/python/cpython/tags)
[![Latest Arrow Version](https://img.shields.io/badge/dynamic/regex?url=https%3A%2F%2Fraw.githubusercontent.com%2Fcorbel-spatial%2Fhere-be-dragons%2Frefs%2Fheads%2Fmain%2Fversions.env&search=(ARROW_VER_LATEST%3D)(.*)&replace=%242&logo=apache&logoColor=orange&label=%20&labelColor=mediumpurple&color=mediumpurple)](https://github.com/apache/arrow/releases)
[![Latest GDAL Version](https://img.shields.io/badge/dynamic/regex?url=https%3A%2F%2Fraw.githubusercontent.com%2Fcorbel-spatial%2Fhere-be-dragons%2Frefs%2Fheads%2Fmain%2Fversions.env&search=(GDAL_VER_LATEST%3D)(.*)&replace=%242&logo=gdal&logoColor=darkgreen&label=GDAL&labelColor=mediumseagreen&color=mediumseagreen)](https://github.com/OSGeo/gdal/releases)
[![GEOS Version](https://img.shields.io/badge/dynamic/regex?url=https%3A%2F%2Fraw.githubusercontent.com%2Fcorbel-spatial%2Fhere-be-dragons%2Frefs%2Fheads%2Fmain%2Fversions.env&search=(GEOS_VER%3D)(.*)&replace=%242&logo=osgeo&logoColor=green&label=GEOS&labelColor=slategray&color=slategray)](https://github.com/libgeos/geos/releases)
[![PROJ Version](https://img.shields.io/badge/dynamic/regex?url=https%3A%2F%2Fraw.githubusercontent.com%2Fcorbel-spatial%2Fhere-be-dragons%2Frefs%2Fheads%2Fmain%2Fversions.env&search=(PROJ_VER%3D)(.*)&replace=%242&logo=osgeo&logoColor=green&label=PROJ&labelColor=slategray&color=slategray)](https://github.com/OSGeo/PROJ/releases)

[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/corbel-spatial/here-be-dragons/build-latest.yml?branch=main)](https://github.com/corbel-spatial/here-be-dragons/actions/workflows/build-latest.yml?query=branch%3Amain)
[![Ubuntu Version](https://img.shields.io/docker/v/_/ubuntu/rolling?logo=ubuntu&logoColor=white&label=ubuntu&labelColor=tomato&color=tomato)](https://hub.docker.com/_/ubuntu)
[![Marimo Version](https://img.shields.io/badge/dynamic/regex?url=https%3A%2F%2Fraw.githubusercontent.com%2Fcorbel-spatial%2Fhere-be-dragons%2Frefs%2Fheads%2Fmain%2Fversions.env&search=(MARIMO_VER%3D)(.*)&replace=%242&label=%F0%9F%8D%83%20%20marimo&labelColor=darkgreen&color=darkgreen)](https://github.com/marimo-team/marimo/releases)
[![Pixi](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fprefix-dev%2Fpixi%2Fmain%2Fassets%2Fbadge%2Fv0.json&label=%E2%9C%A8)](https://pixi.sh)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

This Docker image is the **stable** version intended for production work with common geospatial libraries in the latest version of Python. By default, running the Docker image launches a [marimo](https://marimo.io/) notebook.

To run it in your terminal:

```shell
docker run --name here-be-dragons-latest -p 8080:8080 ghcr.io/corbel-spatial/here-be-dragons:latest
```

## 🔥 Next
[![Next Python Version](https://img.shields.io/badge/dynamic/regex?url=https%3A%2F%2Fraw.githubusercontent.com%2Fcorbel-spatial%2Fhere-be-dragons%2Frefs%2Fheads%2Fmain%2Fversions.env&search=(PYTHON_VER_NEXT%3D)(.*)&replace=%242&logo=python&logoColor=yellow&label=python&labelColor=steelblue&color=steelblue)](https://github.com/python/cpython/tags)
[![Next Arrow Version](https://img.shields.io/badge/dynamic/regex?url=https%3A%2F%2Fraw.githubusercontent.com%2Fcorbel-spatial%2Fhere-be-dragons%2Frefs%2Fheads%2Fmain%2Fversions.env&search=(ARROW_VER_NEXT%3D)(.*)&replace=%242&logo=apache&logoColor=orange&label=%20&labelColor=mediumpurple&color=mediumpurple)](https://github.com/apache/arrow/tags)
[![Next GDAL Version](https://img.shields.io/badge/dynamic/regex?url=https%3A%2F%2Fraw.githubusercontent.com%2Fcorbel-spatial%2Fhere-be-dragons%2Frefs%2Fheads%2Fmain%2Fversions.env&search=(GDAL_VER_NEXT%3D)(.*)&replace=%242&logo=gdal&logoColor=darkgreen&label=GDAL&labelColor=mediumseagreen&color=mediumseagreen)](https://github.com/OSGeo/gdal/tags)
[![GEOS Version](https://img.shields.io/badge/dynamic/regex?url=https%3A%2F%2Fraw.githubusercontent.com%2Fcorbel-spatial%2Fhere-be-dragons%2Frefs%2Fheads%2Fmain%2Fversions.env&search=(GEOS_VER%3D)(.*)&replace=%242&logo=osgeo&logoColor=green&label=GEOS&labelColor=slategray&color=slategray)](https://github.com/libgeos/geos/tags)
[![PROJ Version](https://img.shields.io/badge/dynamic/regex?url=https%3A%2F%2Fraw.githubusercontent.com%2Fcorbel-spatial%2Fhere-be-dragons%2Frefs%2Fheads%2Fmain%2Fversions.env&search=(PROJ_VER%3D)(.*)&replace=%242&logo=osgeo&logoColor=green&label=PROJ&labelColor=slategray&color=slategray)](https://github.com/OSGeo/PROJ/tags)

[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/corbel-spatial/here-be-dragons/build-next.yml?branch=main)](https://github.com/corbel-spatial/here-be-dragons/actions/workflows/build-next.yml?query=branch%3Amain)
[![Ubuntu Version](https://img.shields.io/docker/v/_/ubuntu/rolling?logo=ubuntu&logoColor=white&label=ubuntu&labelColor=tomato&color=tomato)](https://hub.docker.com/_/ubuntu)
[![Marimo Version](https://img.shields.io/badge/dynamic/regex?url=https%3A%2F%2Fraw.githubusercontent.com%2Fcorbel-spatial%2Fhere-be-dragons%2Frefs%2Fheads%2Fmain%2Fversions.env&search=(MARIMO_VER%3D)(.*)&replace=%242&label=%F0%9F%8D%83%20%20marimo&labelColor=darkgreen&color=darkgreen)](https://github.com/marimo-team/marimo/releases)
[![Pixi](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fprefix-dev%2Fpixi%2Fmain%2Fassets%2Fbadge%2Fv0.json&label=%E2%9C%A8)](https://pixi.sh)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

This Docker image is the **experimental** version intended for testing the latest pre-release version of Python against Arrow, GDAL, GEOS, and PROJ. 
Failing builds might indicate that issues are on the horizon.
Some extra packages (`mapclassify`, etc.) may not be included in this image.

```shell
docker run --name here-be-dragons-next -p 8080:8080 ghcr.io/corbel-spatial/here-be-dragons:next
```

## 🚧 To-do List

- Scheduled automatic update of `versions.env` to find new releases/tags
- Add `latest-dev` and `next-dev` variants that keep all the build dependencies
- Add variants built with freethreaded Python (`--disable-gil`)
- Create a benchmark suite and check new releases for performance regressions
- Add more packages upon request - please open an issue!

## 📚 References 

| Project                                                                                           | Source                            | Downstream Packages                                                                                                |
|:--------------------------------------------------------------------------------------------------|:----------------------------------|:-------------------------------------------------------------------------------------------------------------------|
| [Arrow](https://arrow.apache.org/)                                                                | https://github.com/apache/arrow   | [geoarrow-pyarrow](https://geoarrow.org/geoarrow-python/main/index.html)                                           |
| [GDAL](https://gdal.org/)                                                                         | https://github.com/OSGeo/gdal     | [Python bindings](https://pypi.org/project/GDAL/)                                                                  |
| [GEOS](https://libgeos.org/)                                                                      | https://github.com/libgeos/geos   | [Shapely](https://shapely.readthedocs.io/)                                                                         |
| [PROJ](https://proj.org/)                                                                         | https://github.com/OSGeo/PROJ     | [Pyproj](https://pyproj4.github.io/pyproj/stable/)                                                                 |
| [Python](https://www.python.org/)<br/>([release schedule](https://devguide.python.org/versions/)) | https://github.com/python/cpython | [uv](https://docs.astral.sh/uv/), [Pixi](https://pixi.sh/latest/), [marimo](https://github.com/marimo-team/marimo) |
| [Ubuntu](https://ubuntu.com/)                                                                     | https://hub.docker.com/_/ubuntu   |                                                                                                                    |
