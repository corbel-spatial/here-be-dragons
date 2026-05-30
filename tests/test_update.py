import json
from pathlib import Path

import dotenv
import pytest
import update

PKG_NAMES = ["ARROW", "GDAL", "GEOS", "MARIMO", "PROJ", "PYTHON"]


@pytest.fixture
def tag_samples() -> dict:
    return json.loads((Path(__file__).parent / "data" / "tag_samples.json").read_text())


@pytest.fixture
def configs() -> dict:
    return json.loads(update.UPDATE_CONFIG_JSON.read_text())


@pytest.fixture
def vers() -> dict:
    return dotenv.dotenv_values(update.VERSIONS_ENV)


@pytest.mark.parametrize("name", PKG_NAMES)
def test_version(name, tag_samples: dict[str, list], configs) -> None:
    for version in tag_samples[name]:
        config = configs[name]
        update.Version(
            s=version,
            prefix=config["prefix"],
            build_suffixes=config["build_suffixes"],
            prerelease_suffixes=config["prerelease_suffixes"],
        )


def test_parse_configs_vers(configs, vers) -> None:
    packages = update._parse_configs_versions_env(configs, vers)
    assert isinstance(packages, list)
    for pkg in packages:
        assert isinstance(pkg, update.Package)


@pytest.mark.parametrize("name", PKG_NAMES)
@pytest.mark.parametrize("out_path", (Path("./tests/data/atoms"), "tmp_path"))
def test_fetch_tags(name, configs, out_path, request) -> None:
    if out_path == "tmp_path":
        out_path = request.getfixturevalue("tmp_path")

    config = configs[name]
    repo_url = config["repo_url"]
    owner = repo_url.split("/")[3]
    repo = repo_url.split("/")[4]

    latest_tag, next_tag = update.Package._fetch_tags(
        owner=owner,
        repo=repo,
        prefix=config["prefix"],
        build_suffixes=config["build_suffixes"],
        prerelease_suffixes=config["prerelease_suffixes"],
        out_path=out_path,
    )
    if next_tag:
        assert latest_tag < next_tag


def test_version_comparison() -> None:
    build_suffixes = ["-1", "-r2"]
    prerelease_suffixes = ["-rc1", ".dev"]

    release = update.Version(
        "1.0.0",
        build_suffixes=build_suffixes,
        prerelease_suffixes=prerelease_suffixes,
    )
    pre1 = update.Version(
        "1.0.0.dev",
        build_suffixes=build_suffixes,
        prerelease_suffixes=prerelease_suffixes,
    )
    pre2 = update.Version(
        "1.0.0-rc1",
        build_suffixes=build_suffixes,
        prerelease_suffixes=prerelease_suffixes,
    )
    post1 = update.Version(
        "1.0.0-1",
        build_suffixes=build_suffixes,
        prerelease_suffixes=prerelease_suffixes,
    )
    post2 = update.Version(
        "1.0.0-r2",
        build_suffixes=build_suffixes,
        prerelease_suffixes=prerelease_suffixes,
    )

    assert pre1 < pre2 < release < post1 < post2

    versions = [release, pre1, pre2, post1, post2]
    assert str(min(versions)) == "1.0.0.dev"
    assert str(max(versions)) == "1.0.0-r2"
