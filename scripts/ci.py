import argparse

from build import main as build
from update import main as update


def main(
    dry_run: bool,
    no_cache: bool,
    parallel: str,
    push: bool,
    tags: list[str] | None,
    target: str,
    token: str,
    user: str,
) -> None:
    updated = update(
        dry_run=dry_run,
        token=token,
    )

    if updated:
        build(
            dry_run=dry_run,
            no_cache=no_cache,
            parallel=parallel,
            push=push,
            tags=tags,
            target=target,
            token=token,
            user=user,
        )
    else:
        print("\nNothing to do, done")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Here Be Dragons - Update & Build")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Print what would be updated but don't make changes to version.toml",
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
        default=None,
        help="GitHub token for API requests and package push",
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
        dry_run=args.dry_run,
        no_cache=args.no_cache,
        parallel=args.parallel,
        push=args.push,
        tags=run_tags,
        target=args.target,
        token=args.token,
        user=args.user,
    )
