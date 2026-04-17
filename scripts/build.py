import argparse
import os
import subprocess
from pathlib import Path

import tomlkit


def get_tags(pkg_versions: dict[str, str], tag: str, target_name: str) -> list[str]:
    ver_tag = "py" + pkg_versions["PYTHON"][1:]
    ver_tag_short = ".".join(ver_tag.split(".")[0:2])
    if tag == "latest":
        ver_tag_desc = "stable"
    else:
        ver_tag_desc = "experimental"
    return [
        f"{target_name}:{tag}",
        f"{target_name}:{ver_tag_desc}",
        f"{target_name}:{ver_tag_short}",
        f"{target_name}:{ver_tag}",
    ]


def load_versions() -> dict:
    """Load versions from versions.toml"""
    versions_file = Path(__file__).parent.parent / "versions.toml"
    if not versions_file.exists():
        raise FileNotFoundError(
            f"versions.toml not found at {versions_file}. "
            "Please run 'pixi run update' first to generate this file."
        )
    with open(versions_file, "rb") as f:
        versions = tomlkit.load(f)
    return {
        "latest": versions["latest"],
        "next": versions["next"],
    }


def build_dockerfile(
    target: str,
    dockerfile_path: Path,
    pkg_versions: dict,
    parallel: str,
    dry_run: bool = False,
    no_cache: bool = False,
    push: bool = False,
) -> None:
    """Build a Dockerfile with the specified version arguments."""

    # Assemble the command
    tag = dockerfile_path.parent.name
    arg_list = ["docker", "build", "--build-arg", f"PARALLEL={parallel}"]

    for pkg, ver in sorted(pkg_versions.items()):
        # Clean version string (remove surrounding quotes from tomlkit)
        ver_str = str(ver)
        if ver_str.startswith('"') and ver_str.endswith('"'):
            ver_str = ver_str[1:-1]
        arg_list.extend(["--build-arg", f"{pkg}_VER={ver_str}"])

    tags = get_tags(pkg_versions, tag, target)
    for tag in tags:
        arg_list.extend(["-t"])
        arg_list.extend([tag])

    if no_cache:
        arg_list.extend(["--no-cache"])

    if push:
        arg_list.extend(["--push"])

    arg_list.extend(".")
    cmd = " ".join(arg_list)

    # Print the command
    print(f"\n{'[DRY RUN] ' if dry_run else ''}[BUILDING DOCKERFILE] {dockerfile_path}")
    print(cmd)

    if not dry_run:
        try:
            dockerfile_dir = dockerfile_path.parent
            os.chdir(str(dockerfile_dir.resolve()))
            subprocess.run(
                cmd, shell=True, check=True, cwd=str(dockerfile_dir.resolve())
            )
            print(f"✓ Successfully built {target}:{tag}")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to build {target}:{tag}: {e}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build Docker images for here-be-dragons"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print commands but don't build images",
    )
    parser.add_argument(
        "--latest",
        action="store_true",
        help="Only build the latest Dockerfile",
    )
    parser.add_argument(
        "--next",
        action="store_true",
        help="Only build the next Dockerfile",
    )

    parser.add_argument(
        "--parallel",
        default="4",
        help="Number of CPU processes to use (default: 4)",
    )

    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Build with the --no-cache option",
    )

    parser.add_argument(
        "--push",
        action="store_true",
        help="Push to ghcr.io - must provide --token and --user",
    )

    parser.add_argument(
        "--target",
        default="ghcr.io/corbel-spatial/here-be-dragons",
        help="repo/image name",
    )

    parser.add_argument(
        "--token",
        help="token or password for push",
    )

    parser.add_argument(
        "--user",
        help="username for push",
    )

    args = parser.parse_args()

    versions = load_versions()
    if args.parallel:
        parallel = args.parallel
    else:
        parallel = versions["build_args"]["PARALLEL"]

    targets = []
    if args.latest or args.next:
        if args.latest:
            targets.append(Path(__file__).parent.parent / "latest" / "Dockerfile")
        if args.next:
            targets.append(Path(__file__).parent.parent / "next" / "Dockerfile")
    else:
        targets = [
            Path(__file__).parent.parent / "latest" / "Dockerfile",
            Path(__file__).parent.parent / "next" / "Dockerfile",
        ]

    # Authenticate if pushing
    if args.push:
        if not args.token or not args.user:
            raise RuntimeError("Must provide --token and --user for push")
        else:
            print(f"\n[AUTHENTICATING] {args.user}")
            try:
                subprocess.run(
                    ["docker", "login", "ghcr.io", "-u", args.user, "--password-stdin"],
                    input=args.token,
                    text=True,
                    capture_output=True,
                    check=True,
                )
            except subprocess.CalledProcessError:
                print("Authentication failed!")
                return

    # Build
    for dockerfile_path in targets:
        dockerfile_str = str(dockerfile_path)
        dockerfile_tag = "latest" if "latest" in dockerfile_str else "next"
        pkg_versions = versions[dockerfile_tag]
        build_dockerfile(
            target=args.target,
            dockerfile_path=Path(dockerfile_path),
            pkg_versions=pkg_versions,
            parallel=parallel,
            dry_run=args.dry_run,
            no_cache=args.no_cache,
            push=args.push,
        )


if __name__ == "__main__":
    main()
