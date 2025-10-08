# Contributing

## Building the Docker Image

Replace the version arguments (e.g., `PYTHON_VER`) with the branch or release tag to pull from GitHub.
`PARALLEL` sets the number of CPU processes to use for build steps.

```shell
docker build \
    --build-arg PYTHON_VER=v3.14.0 \
    --build-arg GEOS_VER=3.14.0 \
    --build-arg PARALLEL=4 \
    --build-arg PROJ_VER=9.7.0 \
    --build-arg GDAL_VER=v3.11.4 \
    --build-arg ARROW_VER=apache-arrow-21.0.0 \
    -f Dockerfile -t here-be-dragons:latest . && \
docker run -it here-be-dragons:latest
```