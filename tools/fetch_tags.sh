#!/bin/bash

# Exit immediately if a command fails
set -e

# --- 1. Check Dependencies ---
if ! command -v gh &> /dev/null; then
    echo "Error: GitHub CLI ('gh') is not installed."
    exit 1
fi

# --- 2. Configuration ---
# Use positional arguments for owner and repo, with fallbacks
OWNER="${1}"
REPO="${2}"

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Error: Missing required parameters."
    echo "Usage: $0 <owner> <repo>"
    exit 1
fi

LIMIT=100

# --- 3. Fetch and Parse Tags ---
# gh automatically uses your authenticated session
gh api graphql -F owner=$OWNER -F repo=$REPO -f query='
  query($owner: String!, $repo: String!) {
    repository(owner: $owner, name: $repo) {
      refs(refPrefix: "refs/tags/", first: 50, orderBy: {field: TAG_COMMIT_DATE, direction: DESC}) {
        nodes {
          name
        }
      }
    }
  }' --jq '.data.repository.refs.nodes | map(.name)'
