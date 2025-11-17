#!/bin/bash

# Script to close Epic 3 GitHub issues using GitHub CLI
# Prerequisite: Install GitHub CLI (https://cli.github.com/)
# Usage: ./scripts/close_epic3_issues.sh

set -e

# Check if gh is installed
if ! command -v gh &> /dev/null; then
    echo "GitHub CLI (gh) is not installed. Please install it first."
    exit 1
fi

echo 'Closing Epic 3 GitHub issues...'
echo ""

# Epic 3 user stories that are completed:
# US-301: Nearest Neighbor Heuristic
# US-302: 2-Opt Local Search
# US-303: Simulated Annealing Solver
# US-304: Genetic Algorithm Solver (Optional)
# US-305: Algorithm Comparison Framework

# Get all open issues with epic-3 label
echo "Finding all open Epic 3 issues..."
EPIC3_ISSUES=$(gh issue list --label "epic-3" --state open --json number --jq '.[].number')

if [ -z "$EPIC3_ISSUES" ]; then
    echo "No open Epic 3 issues found."
    exit 0
fi

echo "Found the following Epic 3 issues to close:"
echo "$EPIC3_ISSUES"
echo ""

# Close each issue
for issue_number in $EPIC3_ISSUES; do
    echo "Closing issue #$issue_number..."
    gh issue close "$issue_number" --comment "All Epic 3 user stories have been completed. Closing this issue as done."
    echo "✓ Closed issue #$issue_number"
    echo ""
done

echo ""
echo "✓ All Epic 3 issues closed!"
