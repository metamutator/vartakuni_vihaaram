#!/usr/bin/env python3
"""
Script to generate GitHub issues from PROJECT_SPEC.md user stories.

Usage:
    python scripts/generate_github_issues.py

This will create:
1. A markdown file with all issues formatted for GitHub import
2. A JSON file that can be used with GitHub CLI or API
"""

import json
import re
from pathlib import Path


def parse_user_stories(spec_file: Path) -> list[dict]:
    """
    Parse user stories from PROJECT_SPEC.md
    
    Returns list of issue dictionaries with:
    - title
    - body (description)
    - labels
    - milestone (epic)
    - story_points
    """
    
    with open(spec_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the user stories section
    stories_section = re.search(
        r'## 5\. JIRA-Style User Stories.*?(?=##|\Z)', 
        content, 
        re.DOTALL
    )
    
    if not stories_section:
        print("Could not find user stories section")
        return []
    
    stories_text = stories_section.group(0)
    
    # Parse individual user stories
    story_pattern = re.compile(
        r'#### (US-\d+): (.+?)\n'
        r'\*\*As a\*\* (.+?)\n'
        r'\*\*I want to\*\* (.+?)\n'
        r'\*\*So that\*\* (.+?)\n\n'
        r'\*\*Acceptance Criteria:\*\*\n((?:- \[.\] .+\n?)+)\n'
        r'\*\*Story Points:\*\* (\d+)\s+\n'
        r'\*\*Priority:\*\* (\w+)\s+\n'
        r'\*\*Labels:\*\* (.+?)\n',
        re.MULTILINE
    )
    
    stories = []
    
    for match in story_pattern.finditer(stories_text):
        story_id = match.group(1)
        title = match.group(2)
        user = match.group(3)
        action = match.group(4)
        benefit = match.group(5)
        acceptance = match.group(6).strip()
        story_points = match.group(7)
        priority = match.group(8)
        labels = match.group(9)
        
        # Determine epic from story ID
        epic_num = int(story_id.split('-')[1]) // 100
        epic_map = {
            1: "Epic 1: Data Foundation",
            2: "Epic 2: Graph Infrastructure",
            3: "Epic 3: TSP Solver",
            4: "Epic 4: Visualization",
            5: "Epic 5: Deployment",
            6: "Epic 6: Testing",
            7: "Epic 7: Future Enhancements"
        }
        epic = epic_map.get(epic_num, "Uncategorized")
        
        # Format body
        body = f"""**User Story**

As a **{user}**  
I want to **{action}**  
So that **{benefit}**

**Acceptance Criteria**

{acceptance}

**Story Points:** {story_points}  
**Priority:** {priority}
"""
        
        # Parse labels
        label_list = [l.strip() for l in labels.split(',')]
        label_list.append(f"epic-{epic_num}")
        label_list.append(f"priority-{priority.lower()}")
        label_list.append(f"sp-{story_points}")
        
        stories.append({
            'id': story_id,
            'title': f"{story_id}: {title}",
            'body': body,
            'labels': label_list,
            'milestone': epic,
            'story_points': int(story_points),
            'priority': priority
        })
    
    return stories


def generate_markdown_issues(stories: list[dict], output_file: Path):
    """Generate markdown file with issues formatted for manual creation"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# GitHub Issues for Metro TSP Solver\n\n")
        f.write("Copy each issue section below to create GitHub issues manually.\n\n")
        f.write("---\n\n")
        
        for story in stories:
            f.write(f"## {story['title']}\n\n")
            f.write(f"**Labels:** {', '.join(story['labels'])}\n\n")
            f.write(f"**Milestone:** {story['milestone']}\n\n")
            f.write(story['body'])
            f.write("\n\n---\n\n")
    
    print(f"Generated markdown issues: {output_file}")


def generate_json_issues(stories: list[dict], output_file: Path):
    """Generate JSON file for GitHub CLI or API"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(stories, f, indent=2)
    
    print(f"Generated JSON issues: {output_file}")


def generate_gh_cli_script(stories: list[dict], output_file: Path):
    """Generate a shell script that uses GitHub CLI to create issues"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("#!/bin/bash\n\n")
        f.write("# Script to create GitHub issues using GitHub CLI\n")
        f.write("# Prerequisite: Install GitHub CLI (https://cli.github.com/)\n")
        f.write("# Usage: ./scripts/create_github_issues.sh\n\n")
        f.write("# Check if gh is installed\n")
        f.write('if ! command -v gh &> /dev/null; then\n')
        f.write('    echo "GitHub CLI (gh) is not installed. Please install it first."\n')
        f.write('    exit 1\n')
        f.write('fi\n\n')
        f.write("# Create issues\n")
        
        for story in stories:
            # Escape quotes in body
            body_escaped = story['body'].replace('"', '\\"').replace('\n', '\\n')
            labels = ','.join(story['labels'])
            
            f.write(f"\necho 'Creating {story['id']}...'\n")
            f.write(f'gh issue create \\\n')
            f.write(f'  --title "{story["title"]}" \\\n')
            f.write(f'  --body "{body_escaped}" \\\n')
            f.write(f'  --label "{labels}"\n')
            # Note: GitHub CLI doesn't support setting story points directly
            # You may need to use project fields or custom scripts
        
        f.write("\necho 'All issues created!'\n")
    
    # Make script executable
    output_file.chmod(0o755)
    print(f"Generated GitHub CLI script: {output_file}")


def main():
    # Paths
    project_root = Path(__file__).parent.parent
    spec_file = project_root / "PROJECT_SPEC.md"
    output_dir = project_root / "scripts" / "github_issues"
    output_dir.mkdir(exist_ok=True)
    
    # Parse user stories
    print("Parsing user stories from PROJECT_SPEC.md...")
    stories = parse_user_stories(spec_file)
    print(f"Found {len(stories)} user stories")
    
    if not stories:
        print("No stories found. Check the parsing logic.")
        return
    
    # Generate outputs
    generate_markdown_issues(stories, output_dir / "issues.md")
    generate_json_issues(stories, output_dir / "issues.json")
    generate_gh_cli_script(stories, project_root / "scripts" / "create_github_issues.sh")
    
    print("\n✅ Done!")
    print("\nNext steps:")
    print("1. Initialize git repo: cd .. && git init")
    print("2. Create GitHub repo (via web or 'gh repo create')")
    print("3. Push code: git add . && git commit -m 'Initial commit' && git push")
    print("4. Create issues using one of these methods:")
    print("   - Manual: Copy from scripts/github_issues/issues.md")
    print("   - GitHub CLI: ./scripts/create_github_issues.sh")
    print("   - API: Use scripts/github_issues/issues.json with custom script")


if __name__ == "__main__":
    main()
