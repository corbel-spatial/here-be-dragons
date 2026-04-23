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
        f"{target_name}:{ver_tag}",
        f"{target_name}:{ver_tag_short}",
        f"{target_name}:{ver_tag_desc}",
        f"{target_name}:{tag}",
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
    dockerfile_path: Path,
    dry_run: bool,
    no_cache: bool,
    parallel: str,
    pkg_versions: dict,
    platform: str,
    push: bool,
    target: str,
) -> None:
    """Build a Dockerfile with the specified version arguments."""

    # Assemble the command
    tag = dockerfile_path.parent.name
    arg_list = [
        "docker",
        "buildx",
        "build",
        "--pull",
        "--platform",
        platform,
        "--build-arg",
        f"PARALLEL={parallel}",
    ]

    is_ci = os.getenv("GITHUB_ACTIONS") == "true"
    if is_ci:
        cache_scope = f"{tag}-{platform.replace('/', '-')}"
        arg_list.extend(
            [
                "--cache-from",
                f"type=gha,scope={cache_scope}",
                "--cache-to",
                f"type=gha,scope={cache_scope}",
            ]
        )
    else:
        # Local builds keep use the registry (GHCR)
        arg_list.extend(
            [
                "--cache-from",
                f"type=registry,ref={target}:buildcache-{tag}",
                "--cache-to",
                f"type=registry,ref={target}:buildcache-{tag},mode=max",
            ]
        )

    for pkg, ver in sorted(pkg_versions.items()):
        # Clean version string (remove surrounding quotes from tomlkit)
        ver_str = str(ver)
        if ver_str.startswith('"') and ver_str.endswith('"'):
            ver_str = ver_str[1:-1]
        arg_list.extend(["--build-arg", f"{pkg}_VER={ver_str}"])

    for tag in get_tags(pkg_versions, tag, target):
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
            raise RuntimeError(f"Failed to build {target}:{tag}: {e}")


def main(
    amd: bool,
    arm: bool,
    dry_run: bool,
    no_cache: bool,
    parallel: str,
    push: bool,
    tags: list[str] | None,
    target: str,
    token: str,
    user: str,
) -> None:

    versions = load_versions()
    if parallel:
        parallel = parallel
    else:
        parallel = versions["build_args"]["PARALLEL"]

    targets = []
    if len(tags) > 0:
        if "latest" in tags:
            targets.append(Path(__file__).parent.parent / "latest" / "Dockerfile")
        if "next" in tags:
            targets.append(Path(__file__).parent.parent / "next" / "Dockerfile")
    else:
        targets = [
            Path(__file__).parent.parent / "latest" / "Dockerfile",
            Path(__file__).parent.parent / "next" / "Dockerfile",
        ]

    # Authenticate if pushing
    if push:
        if not token or not user:
            raise RuntimeError("Must provide --token and --user for push")
        else:
            print(f"\n[AUTHENTICATING] {user}")
            try:
                subprocess.run(
                    ["docker", "login", "ghcr.io", "-u", user, "--password-stdin"],
                    input=token,
                    text=True,
                    capture_output=True,
                    check=True,
                )
            except subprocess.CalledProcessError:
                print("Authentication failed!")
                return

    # Platform logic and CI Check
    is_ci = os.getenv("GITHUB_ACTIONS") == "true"
    multiarch = False

    if amd and arm:
        platform = "linux/amd64,linux/arm64"
        multiarch = True
    elif amd and not arm:
        platform = "linux/amd64"
    elif arm and not amd:
        platform = "linux/arm64"
    else:
        # default if no flags
        platform = "linux/amd64"

    # Setup buildx driver if utilizing GitHub Actions Cache (is_ci) OR building multiarch
    if multiarch or is_ci:
        print("\n[BUILDX SETUP]")

        # Only install QEMU via binfmt if we are actually cross-compiling
        if multiarch:
            subprocess.run(
                [
                    "docker",
                    "run",
                    "--privileged",
                    "--rm",
                    "tonistiigi/binfmt",
                    "--install",
                    "all",
                ],
                check=True,
            )

        # Create and bootstrap the docker-container driver to support type=gha caching
        subprocess.run(
            ["docker", "buildx", "rm", "multi-builder"], stderr=subprocess.DEVNULL
        )
        subprocess.run(
            [
                "docker",
                "buildx",
                "create",
                "--name",
                "multi-builder",
                "--driver",
                "docker-container",
                "--buildkitd-flags",
                "--allow-insecure-entitlement security.insecure",
                "--use",
            ],
            check=True,
        )
        subprocess.run(
            ["docker", "buildx", "inspect", "multi-builder", "--bootstrap"], check=True
        )

    # Build
    for dockerfile_path in targets:
        dockerfile_str = str(dockerfile_path)
        dockerfile_tag = "latest" if "latest" in dockerfile_str else "next"
        pkg_versions = versions[dockerfile_tag]
        build_dockerfile(
            dockerfile_path=Path(dockerfile_path),
            dry_run=dry_run,
            no_cache=no_cache,
            parallel=parallel,
            pkg_versions=pkg_versions,
            platform=platform,
            push=push,
            target=target,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Here Be Dragons - Build")
    parser.add_argument(
        "--amd",
        action="store_true",
        help="Build amd64 architecture",
    )
    parser.add_argument(
        "--arm",
        action="store_true",
        help="Build arm64 architecture",
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
        "--no-cache",
        action="store_true",
        help="Build with the --no-cache option",
    )
    parser.add_argument(
        "--parallel",
        default="4",
        help="Number of CPU processes to use (default: 4)",
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

    run_tags = list()
    if args.latest:
        run_tags.append("latest")
    if args.next:
        run_tags.append("next")

    main(
        amd=args.amd,
        arm=args.arm,
        dry_run=args.dry_run,
        no_cache=args.no_cache,
        parallel=args.parallel,
        push=args.push,
        tags=run_tags,
        target=args.target,
        token=args.token,
        user=args.user,
    )
