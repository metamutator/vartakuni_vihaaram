#!/bin/bash

# Script to close Epic 3 GitHub issues using GitHub API directly
# Prerequisite: Set GITHUB_TOKEN environment variable
# Usage: GITHUB_TOKEN=your_token ./scripts/close_epic3_issues_api.sh

set -e

# Check if GITHUB_TOKEN is set
if [ -z "$GITHUB_TOKEN" ]; then
    echo "ERROR: GITHUB_TOKEN environment variable is not set."
    echo "Please set it with: export GITHUB_TOKEN=your_github_token"
    exit 1
fi

# Get repository info from git remote
REPO_URL=$(git config --get remote.origin.url)
if [[ $REPO_URL =~ github.com[:/]([^/]+)/([^/.]+) ]]; then
    REPO_OWNER="${BASH_REMATCH[1]}"
    REPO_NAME="${BASH_REMATCH[2]}"
else
    echo "ERROR: Could not parse GitHub repository from git remote."
    exit 1
fi

echo "Repository: $REPO_OWNER/$REPO_NAME"
echo 'Closing Epic 3 GitHub issues...'
echo ""

# GitHub API endpoint
API_BASE="https://api.github.com"

# Get all open issues with epic-3 label
echo "Finding all open Epic 3 issues..."
ISSUES_JSON=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
    -H "Accept: application/vnd.github.v3+json" \
    "$API_BASE/repos/$REPO_OWNER/$REPO_NAME/issues?labels=epic-3&state=open")

# Parse issue numbers
ISSUE_NUMBERS=$(echo "$ISSUES_JSON" | grep -o '"number":[0-9]*' | grep -o '[0-9]*')

if [ -z "$ISSUE_NUMBERS" ]; then
    echo "No open Epic 3 issues found."
    exit 0
fi

echo "Found the following Epic 3 issues to close:"
echo "$ISSUE_NUMBERS"
echo ""

# Close each issue
for issue_number in $ISSUE_NUMBERS; do
    echo "Closing issue #$issue_number..."

    # Close the issue with a comment
    curl -s -X PATCH \
        -H "Authorization: token $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        "$API_BASE/repos/$REPO_OWNER/$REPO_NAME/issues/$issue_number" \
        -d '{"state":"closed"}' > /dev/null

    # Add a closing comment
    curl -s -X POST \
        -H "Authorization: token $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        "$API_BASE/repos/$REPO_OWNER/$REPO_NAME/issues/$issue_number/comments" \
        -d '{"body":"All Epic 3 user stories have been completed. Closing this issue as done."}' > /dev/null

    echo "✓ Closed issue #$issue_number"
    echo ""
done

echo ""
echo "✓ All Epic 3 issues closed!"
