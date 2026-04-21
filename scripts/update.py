import argparse
from pathlib import Path
from time import sleep
from typing import Literal

import semver
import tomlkit
from github import Auth, Github

REPOS = [
    ("apache/arrow", "ARROW"),
    ("OSGeo/gdal", "GDAL"),
    ("libgeos/geos", "GEOS"),
    ("OSGeo/PROJ", "PROJ"),
    ("python/cpython", "PYTHON"),
]

REPO_RELEASE_TAGS: dict[str, list[semver.Version] | None] = {
    repo_path: None for repo_path, _ in REPOS
}


def _parse_tag(tag: str) -> semver.Version | None:
    # v0.0.0-dev -> 0.0.0-dev
    if tag[0].isalpha() and tag[1].isnumeric():
        tag = tag[1:]

    # spam-eggs-0.0.0-dev -> 0.0.0-dev
    for i in range(len(tag)):
        if tag[i].isnumeric():
            tag = tag[i:]
            break

    # 0.0.0a1 -> 0.0.0-a1
    if "-" not in tag and (
        "a" in tag.lower() or "b" in tag.lower() or "c" in tag.lower()
    ):
        for i in range(len(tag) - 1, -1, -1):
            if tag[i].isalpha() and tag[i - 1].isnumeric():
                tag = tag[:i] + "-" + tag[i:]

    # 0-dev -> 0.0.0-dev
    dot_count = len([c for c in tag if c == "."])
    if dot_count != 2:
        if "-" in tag:
            tag, suffix = tag.split("-")
            suffix = "-" + suffix
        else:
            suffix = ""
        match dot_count:
            case 0:
                tag = tag + ".0.0" + suffix
            case 1:
                tag = tag + ".0" + suffix
            case _:
                # give up on edge cases
                tag = None

    if tag.startswith("legacy"):
        tag = None

    if tag:
        return semver.Version.parse(tag)
    else:
        return None


def _fetch_releases(repo_path: str, token: str | None = None) -> list[semver.Version]:
    """Fetch all release metadata from a GitHub repository, sorted by most recent first."""
    if REPO_RELEASE_TAGS[repo_path]:
        return REPO_RELEASE_TAGS[repo_path]

    if token:
        auth = Auth.Token(token)
        gh = Github(auth=auth)
    else:
        gh = Github()
    repo = gh.get_repo(repo_path)

    releases = repo.get_releases()

    release_list = list()
    for release in releases:
        parsed_release = _parse_tag(release.tag_name)
        if parsed_release:
            release_list.append(parsed_release)

    if len(release_list) > 0:
        REPO_RELEASE_TAGS[repo_path] = release_list
        return release_list
    else:  # fallback to tags
        tags = repo.get_tags()
        tag_list = list()
        for tag in tags:
            parsed_tag = _parse_tag(tag.name)
            if parsed_tag:
                tag_list.append(parsed_tag)

        if len(tag_list) == 0:
            raise RuntimeError(f"No releases or tags found: {repo_path}")
        else:
            REPO_RELEASE_TAGS[repo_path] = tag_list
            return tag_list


def fetch_latest_release(repo_path: str, token: str | None = None) -> str:
    """Fetch the latest stable release from a GitHub repository."""
    releases_list = _fetch_releases(repo_path, token)
    stable_releases = [r for r in releases_list if not r.prerelease]
    return str(max(stable_releases))


def fetch_next_release(repo_path: str, token: str | None = None) -> str:
    """Fetch the latest unstable release from a GitHub repository, or latest stable if it's newer."""
    releases_list = _fetch_releases(repo_path, token)

    releases = [r for r in releases_list if not r.prerelease]
    newest_stable_release = max(releases)

    prereleases = [r for r in releases_list if r.prerelease]
    if len(prereleases) == 0:
        return str(newest_stable_release)

    newest_prerelease = max(prereleases)
    if newest_prerelease > newest_stable_release:
        return str(newest_prerelease)
    else:
        return str(newest_stable_release)


def _update_version(
    pkg: str,
    version: str,
    tag: Literal["latest", "next"],
) -> None:
    """Replace the package version in versions.toml and README.md."""
    versions_file = Path(__file__).parent.parent / "versions.toml"

    with open(versions_file, "rb") as f:
        versions: dict[str, dict[str, str]] = tomlkit.load(f)

    lookup = versions["latest"] if tag == "latest" else versions["next"]
    lookup[pkg] = version

    versions_string = tomlkit.dumps(versions)
    with open(versions_file, "wb") as f:
        f.write(versions_string.encode())


def update_latest(
    pkg: str,
    version: str,
) -> None:
    _update_version(
        pkg,
        version,
        "latest",
    )


def update_next(
    pkg: str,
    version: str,
) -> None:
    _update_version(
        pkg,
        version,
        "next",
    )


def main(
    dry_run: bool = False,
    token: str | None = None,
) -> bool:
    print("Here Be Dragons - Check and Update Releases\n")

    project_root = Path(__file__).parent.parent
    latest_dockerfile = project_root / "latest" / "Dockerfile"
    next_dockerfile = project_root / "next" / "Dockerfile"
    versions_file = project_root / "versions.toml"

    for file in (latest_dockerfile, next_dockerfile, versions_file):
        if not file.exists():
            raise FileNotFoundError(f"File {file} does not exist")

    print(f"Project root: {project_root}")
    print(f"Dockerfile for latest: {latest_dockerfile}")
    print(f"Dockerfile for next: {next_dockerfile}")
    print(f"Versions file: {versions_file}")

    with open(versions_file, "rb") as f:
        versions: dict[str, dict[str, str]] = tomlkit.load(f)

    latest_lookup = versions["latest"]
    next_lookup = versions["next"]

    print("\nCurrent versions in versions.toml:")

    print("\nLatest")
    for pkg, ver in latest_lookup.items():
        print(f"  - {pkg}: {ver}")
    print("\nNext")
    for pkg, ver in next_lookup.items():
        print(f"  - {pkg}: {ver}")

    print("\n\nChecking for new versions. ..")

    updated = False
    for repo_path, pkg in REPOS:
        print(f"\nFetching {pkg} releases from https://github.com/{repo_path}")

        latest_release = fetch_latest_release(repo_path, token)
        latest_lookup_pkg = latest_lookup[pkg]

        next_release = fetch_next_release(repo_path, token)
        next_lookup_pkg = next_lookup[pkg]

        if pkg == "ARROW":
            latest_release = "apache-arrow-" + latest_release
            next_release = "apache-arrow-" + next_release

        if pkg in ("GDAL", "PYTHON"):
            latest_release = "v" + latest_release
            next_release = "v" + next_release.replace("-", "")

        if latest_release != latest_lookup_pkg:
            updated = True
            print(f" - {pkg} latest {latest_lookup_pkg} -> {latest_release}")
            if dry_run:
                print("       [DRY RUN] Would update to: " + latest_release)
            else:
                update_latest(pkg, latest_release)
        else:
            print(f" - New stable version not found, currently {latest_release}")

        if next_release != next_lookup_pkg:
            updated = True
            print(f" - {pkg} next {next_lookup_pkg} -> {next_release}")
            if dry_run:
                print("       [DRY RUN] Would update to: " + next_release)
            else:
                update_next(pkg, next_release)
        else:
            print(f" - New experimental version not found, currently {next_release}")

        sleep(1)

    return updated


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Here Be Dragons - Update")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Print what would be updated but don't make changes to version.toml",
    )
    parser.add_argument(
        "--token",
        default=None,
        help="GitHub token for API requests",
    )
    args = parser.parse_args()

    main(dry_run=args.dry_run, token=args.token)
