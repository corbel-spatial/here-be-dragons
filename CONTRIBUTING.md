# Contributing

For testing and development work you can build the Docker images locally.

The easiest way is to [install Pixi](https://pixi.prefix.dev/latest/installation/) and use one of the tasks defined in [pixi.toml](pixi.toml).
The build argument `PARALLEL` sets the number of CPU processes to use.

```shell
pixi run build-latest --build-arg PARALLEL=4
docker run -it here-be-dragons:latest
```
