import json
import tempfile
import urllib.request
import xml.etree.ElementTree as ET  # noqa
from dataclasses import dataclass
from functools import total_ordering
from pathlib import Path
from typing import Any, Iterable

import dotenv
import semver

UPDATE_CONFIG_JSON = Path(__file__).parent / "update_config.json"
VERSIONS_ENV = Path(__file__).parent.parent / "versions.env"


@dataclass
@total_ordering
class Version:
    major: int = 0
    minor: int = 0
    patch: int = 0
    prefix: str | None = None
    suffix: str | None = None
    suffix_sep: str | None = None
    prerelease: bool | None = None
    postrelease: bool | None = None

    def __init__(
        self,
        s: str | None = None,
        prefix: str | None = None,
        build_suffixes: Iterable | None = None,
        prerelease_suffixes: Iterable | None = None,
    ) -> None:
        if not s:
            # create an empty object
            return

        s_init = s

        if prefix:
            if not s.startswith(prefix):
                # if invalid, return empty object
                return
            else:
                s = s[len(prefix) :]
                self.prefix = prefix

        if prerelease_suffixes:
            for suffix in prerelease_suffixes:
                if s.endswith(suffix):
                    self.suffix = suffix
                    self.prerelease = True
                    self.postrelease = False
                    break

        if not self.prerelease:
            self.prerelease = False
            self.postrelease = False

        if not self.suffix and build_suffixes:
            for suffix in build_suffixes:
                if s.endswith(suffix):
                    self.suffix = suffix
                    self.postrelease = True
                    break

        if self.suffix:
            s = s[: -len(self.suffix)]
            if not self.suffix[0].isalpha():
                self.suffix_sep = self.suffix[0]
                self.suffix = self.suffix[1:]
            else:
                self.suffix_sep = ""

        sver: dict = semver.Version.parse(s).to_dict()
        self.major = sver["major"]
        self.minor = sver["minor"]
        self.patch = sver["patch"]
        assert self.__str__() == s_init, ValueError(
            f"Version parts ({self.__repr__()}) should compose input string '{s_init}'"
        )

    def __str__(self) -> str:
        return f"{self.prefix}{self.major}.{self.minor}.{self.patch}{self.suffix_sep}{self.suffix}".replace(
            "None", ""
        )

    def _comparison_key(self) -> tuple:
        if self.prerelease:
            release_tier = 0
        elif self.postrelease:
            release_tier = 2
        else:
            release_tier = 1

        return (
            self.major,
            self.minor,
            self.patch,
            release_tier,
            self.suffix or "",
            self.prefix or "",
        )

    def __lt__(self, other: "Version") -> bool:
        return self._comparison_key() < other._comparison_key()

    def __eq__(self, other: "Version") -> bool:
        return self._comparison_key() == other._comparison_key()


@dataclass
class Package:
    name: str
    nice_name: str
    repo_url: str
    latest_version: Version
    next_version: Version | None
    modified: bool = False

    def __init__(self, config: dict[str, Any], vers: dict[str, Any]) -> None:
        self.name = config["name"]
        self.nice_name = config["nice_name"]
        self.repo_url = config["repo_url"]
        self.requires_next = config["next"]

        self.prefix = config["prefix"]
        self.build_suffixes = config["build_suffixes"]
        self.prerelease_suffixes = config["prerelease_suffixes"]

        if config["next"]:
            self.latest_version = Version(
                vers[f"{self.name}_VER_LATEST"],
                self.prefix,
                build_suffixes=self.build_suffixes,
            )
            self.next_version = Version(
                vers[f"{self.name}_VER_NEXT"],
                self.prefix,
                prerelease_suffixes=self.prerelease_suffixes,
            )
        else:
            self.latest_version = Version(
                vers[f"{self.name}_VER"],
                self.prefix,
                build_suffixes=self.build_suffixes,
            )
            self.next_version = None

    def refresh(self, out_path: Path | None = None) -> None:
        """Make and API call to the repo_url and update the stable and prerelease versions as needed."""
        owner = self.repo_url.split("/")[3]
        repo = self.repo_url.split("/")[4]
        latest_version, next_version = self._fetch_tags(
            owner=owner,
            repo=repo,
            prefix=self.prefix,
            build_suffixes=self.build_suffixes,
            prerelease_suffixes=self.prerelease_suffixes,
            out_path=out_path,
        )

        self.modified = False
        if latest_version != self.latest_version:
            self.latest_version = latest_version
            self.modified = True

        if not next_version and self.next_version and self.requires_next:
            self.next_version = latest_version
            self.modified = True

        if next_version and next_version != self.next_version:
            self.next_version = next_version
            self.modified = True

    @staticmethod
    def _fetch_tags(
        owner: str,
        repo: str,
        prefix: str | None = None,
        build_suffixes: Iterable | None = None,
        prerelease_suffixes: Iterable | None = None,
        out_path: Path | None = None,
    ) -> tuple[Version, Version | None]:
        url = f"https://github.com/{owner}/{repo}/tags.atom"

        if not out_path:
            file = Path(tempfile.gettempdir()) / f"{repo.upper()}_tags.atom"
        else:
            file = out_path / f"{repo.upper()}_tags.atom"

        if not file.exists():
            urllib.request.urlretrieve(url, file)

        root = ET.parse(file).getroot()

        namespaces = {"atom": "http://www.w3.org/2005/Atom"}
        versions: list[Version] = []
        for entry in root.findall("atom:entry", namespaces):
            link = entry.find("atom:link", namespaces)
            href = link.get("href")  # noqa
            tag = href.split("/")[-1]  # noqa
            versions.append(
                Version(
                    s=tag,
                    prefix=prefix,
                    build_suffixes=build_suffixes,
                    prerelease_suffixes=prerelease_suffixes,
                )
            )

        versions = sorted(versions, reverse=True)
        max_ver = versions[0]

        if not max_ver.prerelease:
            latest_tag = max_ver
            next_tag = None
        else:
            next_tag = max_ver
            latest_tag = max([ver for ver in versions if not ver.prerelease])

        return latest_tag, next_tag

    def write_env(self, fp) -> None:
        """Write the object's versions to the supplied fp"""
        if self.requires_next:
            dotenv.set_key(
                fp,
                f"{self.name}_VER_LATEST",
                str(self.latest_version),
                quote_mode="never",
            )
            dotenv.set_key(
                fp, f"{self.name}_VER_NEXT", str(self.next_version), quote_mode="never"
            )
        else:
            dotenv.set_key(
                fp, f"{self.name}_VER", str(self.latest_version), quote_mode="never"
            )

        if self.name == "PYTHON":
            dotenv.set_key(
                fp,
                "LATEST_TAG",
                f"{self.latest_version.major}.{self.latest_version.minor}.{self.latest_version.patch}",
                quote_mode="never",
            )
            dotenv.set_key(
                fp,
                "LATEST_TAG_SHORT",
                f"{self.latest_version.major}.{self.latest_version.minor}",
                quote_mode="never",
            )

            assert isinstance(self.next_version, Version)
            dotenv.set_key(
                fp,
                "NEXT_TAG",
                f"{self.next_version.major}.{self.next_version.minor}.{self.next_version.patch}{self.next_version.suffix}",
                quote_mode="never",
            )
            dotenv.set_key(
                fp,
                "NEXT_TAG_SHORT",
                f"{self.next_version.major}.{self.next_version.minor}",
                quote_mode="never",
            )


def _parse_configs_versions_env(configs, vers) -> list[Package]:
    packages: list[Package] = list()
    for config in configs.values():
        pkg = Package(config, vers)
        packages.append(pkg)
        print()
        print(pkg.nice_name)
        if pkg.next_version:
            print(f" - latest: {pkg.latest_version} {pkg.latest_version.__repr__()}")
            print(f" - next:   {pkg.next_version} {pkg.next_version.__repr__()}")
        else:
            print(f" - {pkg.latest_version} {pkg.latest_version.__repr__()}")
    return packages


def _refresh_packages(packages: list[Package]) -> None:
    for pkg in packages:
        pkg.refresh()
        if pkg.modified:
            pkg.write_env(VERSIONS_ENV)


def main() -> None:  # pragma: no cover
    configs = json.loads(UPDATE_CONFIG_JSON.read_text())
    vers = dotenv.dotenv_values(VERSIONS_ENV)

    packages = _parse_configs_versions_env(configs, vers)

    _refresh_packages(packages)


if __name__ == "__main__":  # pragma: no cover
    main()
