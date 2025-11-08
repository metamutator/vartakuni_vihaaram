#!/usr/bin/env python3
"""
Script to generate GitHub issues from PROJECT_SPEC.md user stories.

Usage:
    python scripts/generate_github_issues.py
"""

import json
import re
from pathlib import Path


def main():
    # Paths
    project_root = Path(__file__).parent.parent
    spec_file = project_root / "PROJECT_SPEC.md"
    output_dir = project_root / "scripts" / "github_issues"
    output_dir.mkdir(exist_ok=True)
    
    print("Parsing user stories from PROJECT_SPEC.md...")
    
    with open(spec_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find user stories section
    start_marker = "## 5. JIRA-Style User Stories"
    end_marker = "\n## 6."
    
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker, start_idx)
    
    if start_idx == -1:
        print("Could not find user stories section")
        return
    
    if end_idx == -1:
        end_idx = len(content)
    
    stories_section = content[start_idx:end_idx]
    
    # Split by ### Epic headers to process each epic
    epic_sections = re.split(r'(### Epic \d+: .+)', stories_section)
    
    all_issues = []
    
    # Process pairs of (epic header, epic content)
    for i in range(1, len(epic_sections), 2):
        if i + 1 >= len(epic_sections):
            break
            
        epic_header = epic_sections[i]
        epic_content = epic_sections[i + 1]
        
        # Extract epic number and name
        epic_match = re.match(r'### Epic (\d+): (.+)', epic_header)
        if not epic_match:
            continue
        
        epic_num = epic_match.group(1)
        epic_name = epic_match.group(2).strip()
        
        # Split by ---  to get individual stories
        story_blocks = epic_content.split('\n---\n')
        
        for block in story_blocks:
            block = block.strip()
            if not block or not block.startswith('####'):
                continue
            
            # Parse story
            lines = block.split('\n')
            
            # Extract header
            header_match = re.match(r'#### (US-\d+): (.+)', lines[0])
            if not header_match:
                continue
            
            story_id = header_match.group(1)
            story_title = header_match.group(2).strip()
            
            # Extract user story components
            user_story = {}
            acceptance_criteria = []
            in_acceptance = False
            metadata = {}
            
            for line in lines[1:]:
                line = line.strip()
                
                if line.startswith('**As a**'):
                    user_story['user'] = line.replace('**As a**', '').strip()
                elif line.startswith('**I want to**'):
                    user_story['action'] = line.replace('**I want to**', '').strip()
                elif line.startswith('**So that**'):
                    user_story['benefit'] = line.replace('**So that**', '').strip()
                elif line == '**Acceptance Criteria:**':
                    in_acceptance = True
                elif in_acceptance and line.startswith('- [ ]'):
                    acceptance_criteria.append(line)
                elif line.startswith('**Story Points:**'):
                    metadata['story_points'] = line.split('**Story Points:**')[1].strip()
                    in_acceptance = False
                elif line.startswith('**Priority:**'):
                    metadata['priority'] = line.split('**Priority:**')[1].strip()
                elif line.startswith('**Labels:**'):
                    metadata['labels'] = line.split('**Labels:**')[1].strip()
            
            # Skip if incomplete
            if not all([user_story.get('user'), user_story.get('action'), 
                       user_story.get('benefit'), metadata.get('story_points')]):
                continue
            
            # Build issue
            labels = [l.strip() for l in metadata['labels'].split(',')]
            labels.extend([f"epic-{epic_num}", f"priority-{metadata['priority'].lower()}"])
            
            body = f"""**User Story**

As a **{user_story['user']}**  
I want to **{user_story['action']}**  
So that **{user_story['benefit']}**

**Acceptance Criteria**

{chr(10).join(acceptance_criteria)}

**Story Points:** {metadata['story_points']}  
**Priority:** {metadata['priority']}
"""
            
            issue = {
                'id': story_id,
                'title': f"{story_id}: {story_title}",
                'body': body,
                'labels': labels,
                'milestone': f"Epic {epic_num}: {epic_name}",
                'story_points': metadata['story_points'],
                'priority': metadata['priority']
            }
            
            all_issues.append(issue)
    
    print(f"Found {len(all_issues)} user stories")
    
    if not all_issues:
        print("No stories found.")
        return
    
    # Generate markdown file
    md_output = output_dir / "issues.md"
    with open(md_output, 'w', encoding='utf-8') as f:
        f.write("# GitHub Issues for Metro TSP Solver\n\n")
        f.write("Copy each issue section below to create GitHub issues manually.\n\n")
        f.write("---\n\n")
        
        for issue in all_issues:
            f.write(f"## {issue['title']}\n\n")
            f.write(f"**Labels:** {', '.join(issue['labels'])}\n\n")
            f.write(f"**Milestone:** {issue['milestone']}\n\n")
            f.write(issue['body'])
            f.write("\n\n---\n\n")
    
    print(f"✓ Generated: {md_output}")
    
    # Generate JSON file
    json_output = output_dir / "issues.json"
    with open(json_output, 'w', encoding='utf-8') as f:
        json.dump(all_issues, f, indent=2)
    
    print(f"✓ Generated: {json_output}")
    
    # Generate GitHub CLI script
    script_output = project_root / "scripts" / "create_github_issues.sh"
    with open(script_output, 'w', encoding='utf-8') as f:
        f.write("#!/bin/bash\n\n")
        f.write("# Script to create GitHub issues using GitHub CLI\n")
        f.write("# Prerequisite: Install GitHub CLI (https://cli.github.com/)\n")
        f.write("# Usage: ./scripts/create_github_issues.sh\n\n")
        f.write("set -e\n\n")
        f.write("# Check if gh is installed\n")
        f.write('if ! command -v gh &> /dev/null; then\n')
        f.write('    echo "GitHub CLI (gh) is not installed. Please install it first."\n')
        f.write('    exit 1\n')
        f.write('fi\n\n')
        f.write("echo 'Creating GitHub issues...'\n")
        f.write('echo ""\n\n')
        
        for issue in all_issues:
            # Escape body for shell
            body_escaped = issue['body'].replace('\\', '\\\\').replace('"', '\\"').replace('$', '\\$').replace('`', '\\`')
            labels = ','.join(issue['labels'])
            
            f.write(f"echo 'Creating {issue['id']}: {issue['title'][:50]}...'\n")
            f.write('gh issue create \\\n')
            f.write(f'  --title "{issue["title"]}" \\\n')
            f.write(f'  --body "{body_escaped}" \\\n')
            f.write(f'  --label "{labels}"\n')
            f.write('echo ""\n\n')
        
        f.write('echo ""\n')
        f.write('echo "✓ All issues created!"\n')
    
    # Make script executable
    script_output.chmod(0o755)
    print(f"✓ Generated: {script_output}")
    
    print("\n✅ Done!")
    print("\nNext steps:")
    print("1. Review issues in: scripts/github_issues/issues.md")
    print("2. Create issues using either:")
    print("   • GitHub CLI: ./scripts/create_github_issues.sh")
    print("   • Manual: Copy from scripts/github_issues/issues.md")


if __name__ == "__main__":
    main()
