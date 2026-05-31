import json
from pathlib import Path
from unittest.mock import patch

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


def test_version_init() -> None:
    empty_ver = update.Version()
    assert empty_ver.major == 0

    basic_ver = update.Version("1.0.0")
    assert empty_ver < basic_ver


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


def test_package_refresh_updates(configs, vers, tmp_path) -> None:
    pkg = update.Package(config=configs["PYTHON"], vers=vers)

    new_latest = update.Version("3.15.0", prefix="v")
    new_next = update.Version("3.15.0a1", prefix="v")

    with patch("update.Package._fetch_tags", return_value=(new_latest, new_next)):
        pkg.refresh()

    assert pkg.modified is True
    assert pkg.latest_version == new_latest
    assert pkg.next_version == new_next

    pkg = update.Package(config=configs["PYTHON"], vers=vers)
    pkg.next_version = update.Version("3.16.0", prefix="v")

    with patch("update.Package._fetch_tags", return_value=(new_latest, None)):
        pkg.refresh()

    assert pkg.modified is True
    assert pkg.next_version == new_latest

    pkg2 = update.Package(config=configs["MARIMO"], vers=vers)
    pkg2.refresh(out_path=Path("./tests/data/atoms"))
    pkg2.refresh()
    pkg2.write_env(tmp_path / "test.env")


def test_python_write_env(configs, vers, tmp_path) -> None:
    pkg = update.Package(config=configs["PYTHON"], vers=vers)
    env_file = tmp_path / "python_test.env"
    pkg.write_env(env_file)

    written_values = dotenv.dotenv_values(env_file)
    assert written_values["PYTHON_VER_LATEST"] == str(pkg.latest_version)
    assert written_values["PYTHON_VER_NEXT"] == str(pkg.next_version)
    assert (
        written_values["LATEST_TAG"]
        == f"{pkg.latest_version.major}.{pkg.latest_version.minor}.{pkg.latest_version.patch}"
    )
    assert (
        written_values["LATEST_TAG_SHORT"]
        == f"{pkg.latest_version.major}.{pkg.latest_version.minor}"
    )
    assert isinstance(pkg.next_version, update.Version)
    assert (
        written_values["NEXT_TAG"]
        == f"{pkg.next_version.major}.{pkg.next_version.minor}.{pkg.next_version.patch}{pkg.next_version.suffix}"
    )
    assert (
        written_values["NEXT_TAG_SHORT"]
        == f"{pkg.next_version.major}.{pkg.next_version.minor}"
    )


def test_refresh_packages(configs, vers, tmp_path) -> None:
    pkg = update.Package(config=configs["GEOS"], vers=vers)
    fake_env = tmp_path / "versions.env"
    fake_env.write_text("GEOS_VER=3.13.0\n")

    new_latest = update.Version("3.14.1")

    def mock_refresh(self) -> None:
        self.latest_version = new_latest
        self.modified = True

    with (
        patch("update.Package.refresh", mock_refresh),
        patch("update.VERSIONS_ENV", fake_env),
    ):
        update._refresh_packages([pkg])

    assert pkg.modified is True
    assert pkg.latest_version == new_latest

    written = dotenv.dotenv_values(fake_env)
    assert written["GEOS_VER"] == "3.14.1"


def test_refresh_packages_not_modified(configs, vers, tmp_path) -> None:
    pkg = update.Package(config=configs["GEOS"], vers=vers)
    fake_env = tmp_path / "versions.env"
    fake_env.write_text("GEOS_VER=3.14.1\n")

    def mock_refresh_no_change(self) -> None:
        self.modified = False

    with (
        patch("update.Package.refresh", mock_refresh_no_change),
        patch("update.VERSIONS_ENV", fake_env),
    ):
        update._refresh_packages([pkg])

    assert pkg.modified is False
    written = dotenv.dotenv_values(fake_env)
    assert written["GEOS_VER"] == "3.14.1"
