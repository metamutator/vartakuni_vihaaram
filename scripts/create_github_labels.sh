#!/bin/bash

# Script to create GitHub labels for the project
# Usage: ./scripts/create_github_labels.sh

set -e

echo "Creating GitHub labels..."
echo ""

# Check if gh is installed
if ! command -v gh &> /dev/null; then
    echo "GitHub CLI (gh) is not installed. Please install it first."
    exit 1
fi

# Epic labels
gh label create "epic-1" --description "Epic 1: Data Foundation" --color "0E8A16" 2>/dev/null || echo "Label 'epic-1' already exists"
gh label create "epic-2" --description "Epic 2: Graph Infrastructure" --color "0E8A16" 2>/dev/null || echo "Label 'epic-2' already exists"
gh label create "epic-3" --description "Epic 3: TSP Solver" --color "0E8A16" 2>/dev/null || echo "Label 'epic-3' already exists"
gh label create "epic-4" --description "Epic 4: Visualization" --color "0E8A16" 2>/dev/null || echo "Label 'epic-4' already exists"
gh label create "epic-5" --description "Epic 5: Deployment" --color "0E8A16" 2>/dev/null || echo "Label 'epic-5' already exists"
gh label create "epic-6" --description "Epic 6: Testing" --color "0E8A16" 2>/dev/null || echo "Label 'epic-6' already exists"
gh label create "epic-7" --description "Epic 7: Future Enhancements" --color "0E8A16" 2>/dev/null || echo "Label 'epic-7' already exists"
gh label create "epic-8" --description "Epic 8: SVG Map Integration" --color "0E8A16" 2>/dev/null || echo "Label 'epic-8' already exists"

# Priority labels
gh label create "priority-high" --description "High priority" --color "D93F0B" 2>/dev/null || echo "Label 'priority-high' already exists"
gh label create "priority-medium" --description "Medium priority" --color "FBCA04" 2>/dev/null || echo "Label 'priority-medium' already exists"
gh label create "priority-low" --description "Low priority" --color "0075CA" 2>/dev/null || echo "Label 'priority-low' already exists"

# Phase labels
gh label create "phase-1" --description "Phase 1: MVP" --color "C2E0C6" 2>/dev/null || echo "Label 'phase-1' already exists"
gh label create "phase-2" --description "Phase 2: Enhancements" --color "BFDADC" 2>/dev/null || echo "Label 'phase-2' already exists"

# Category labels
gh label create "data-collection" --description "Data gathering and preparation" --color "5319E7" 2>/dev/null || echo "Label 'data-collection' already exists"
gh label create "backend" --description "Backend/core logic" --color "1D76DB" 2>/dev/null || echo "Label 'backend' already exists"
gh label create "graph" --description "Graph theory and network modeling" --color "006B75" 2>/dev/null || echo "Label 'graph' already exists"
gh label create "algorithm" --description "TSP and optimization algorithms" --color "B60205" 2>/dev/null || echo "Label 'algorithm' already exists"
gh label create "visualization" --description "Maps and plotting" --color "E99695" 2>/dev/null || echo "Label 'visualization' already exists"
gh label create "svg" --description "SVG-specific tasks" --color "0052CC" 2>/dev/null || echo "Label 'svg' already exists"
gh label create "frontend" --description "User interface" --color "FBCA04" 2>/dev/null || echo "Label 'frontend' already exists"
gh label create "deployment" --description "Deployment and CI/CD" --color "C5DEF5" 2>/dev/null || echo "Label 'deployment' already exists"
gh label create "testing" --description "Unit and integration tests" --color "D4C5F9" 2>/dev/null || echo "Label 'testing' already exists"
gh label create "documentation" --description "Documentation" --color "0075CA" 2>/dev/null || echo "Label 'documentation' already exists"
gh label create "validation" --description "Data validation" --color "D876E3" 2>/dev/null || echo "Label 'validation' already exists"
gh label create "quarto" --description "Quarto website" --color "F9D0C4" 2>/dev/null || echo "Label 'quarto' already exists"
gh label create "devops" --description "DevOps and tooling" --color "BFD4F2" 2>/dev/null || echo "Label 'devops' already exists"
gh label create "research" --description "Research and exploration" --color "D4C5F9" 2>/dev/null || echo "Label 'research' already exists"
gh label create "analysis" --description "Analysis and benchmarking" --color "C5DEF5" 2>/dev/null || echo "Label 'analysis' already exists"
gh label create "interaction" --description "User interaction features" --color "FBCA04" 2>/dev/null || echo "Label 'interaction' already exists"
gh label create "integration" --description "Integration testing" --color "D4C5F9" 2>/dev/null || echo "Label 'integration' already exists"
gh label create "enhancement" --description "New feature or request" --color "A2EEEF" 2>/dev/null || echo "Label 'enhancement' already exists"
gh label create "automation" --description "Automation scripts" --color "BFD4F2" 2>/dev/null || echo "Label 'automation' already exists"
gh label create "optional" --description "Optional feature" --color "E4E669" 2>/dev/null || echo "Label 'optional' already exists"

echo ""
echo "✓ All labels created!"
echo ""
echo "You can now run: ./scripts/create_github_issues.sh"
