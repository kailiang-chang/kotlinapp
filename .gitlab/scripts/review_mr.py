#!/usr/bin/env python3
"""
GitLab MR Review Script using Grok API
Equivalent to GitHub's claude-code-action for GitLab CI/CD
"""

import os
import sys
from openai import OpenAI
import requests
from pathlib import Path
import urllib3

# Disable SSL warnings when verify=False is used
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration from environment variables
GITLAB_TOKEN = os.environ.get('GITLAB_TOKEN')
GITLAB_API_URL = os.environ.get('CI_API_V4_URL', 'https://gitlab.com/api/v4')
PROJECT_ID = os.environ.get('CI_PROJECT_ID')
XAI_API_KEY = os.environ.get('XAI_API_KEY')
POST_COMMENT = os.environ.get('POST_COMMENT', 'false').lower() == 'true'

def get_mr_diff(mr_number):
    """Fetch MR diff from GitLab API"""
    url = f"{GITLAB_API_URL}/projects/{PROJECT_ID}/merge_requests/{mr_number}/diffs"
    headers = {'PRIVATE-TOKEN': GITLAB_TOKEN}

    response = requests.get(url, headers=headers, verify=False)
    response.raise_for_status()

    diffs = response.json()

    # Format diffs similar to `gh pr diff` output
    diff_text = ""
    for diff in diffs:
        if not should_review_file(diff['new_path']):
            continue

        diff_text += f"\n--- a/{diff['old_path']}\n"
        diff_text += f"+++ b/{diff['new_path']}\n"
        diff_text += diff['diff'] + "\n"

    return diff_text

def should_review_file(filepath):
    """Check if file matches review patterns"""
    extensions = ['.kt', '.java', '.gradle', '.xml']
    return any(filepath.endswith(ext) for ext in extensions)

def get_mr_info(mr_number):
    """Fetch MR metadata"""
    url = f"{GITLAB_API_URL}/projects/{PROJECT_ID}/merge_requests/{mr_number}"
    headers = {'PRIVATE-TOKEN': GITLAB_TOKEN}

    response = requests.get(url, headers=headers, verify=False)
    response.raise_for_status()

    return response.json()

def review_with_grok(mr_number, diff_text, mr_info):
    """Send diff to Grok for review"""
    client = OpenAI(
        api_key=XAI_API_KEY,
        base_url="https://api.x.ai/v1"
    )

    prompt = f"""You are a careful MR reviewer.

MR #{mr_number}: {mr_info['title']}
Repository: {mr_info['references']['full']}

Goal:
- Review this merge request diff.
- ONLY analyze files matching these patterns: **/*.kt, **/*.java, **/*.gradle, **/*.xml (Android layout/manifest files)
- Skip all other files (markdown, images, config files, etc.)
- Analyze the diff and run lightweight checks (no builds): lint-like reasoning, potential bugs, risky changes.
- Produce a concise markdown report with:
  - Summary
  - Strengths
  - Risks / Potential bugs
  - Suggested minimal patch as a unified diff inside a fenced code block
  - Next actions for the author

Here is the diff:

```diff
{diff_text}
```

Generate the review report now."""

    completion = client.chat.completions.create(
        model="grok-4-1-fast",
        max_tokens=4096,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return completion.choices[0].message.content

def save_report(mr_number, review_text):
    """Save review report to file"""
    reports_dir = Path('reports')
    reports_dir.mkdir(exist_ok=True)

    report_path = reports_dir / f'mr-{mr_number}-review.md'
    report_path.write_text(review_text)

    print(f"✅ Review report saved to: {report_path}")
    return report_path

def post_mr_comment(mr_number, report_path):
    """Post comment on MR with link to report"""
    url = f"{GITLAB_API_URL}/projects/{PROJECT_ID}/merge_requests/{mr_number}/notes"
    headers = {'PRIVATE-TOKEN': GITLAB_TOKEN}

    comment_body = f"📄 Review report generated and attached as pipeline artifact: `{report_path}`"

    response = requests.post(
        url,
        headers=headers,
        json={'body': comment_body},
        verify=False
    )
    response.raise_for_status()

    print(f"✅ Comment posted to MR #{mr_number}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python review_mr.py <MR_NUMBER>")
        sys.exit(1)

    mr_number = sys.argv[1]

    # Validate environment
    if not all([GITLAB_TOKEN, PROJECT_ID, XAI_API_KEY]):
        print("❌ Missing required environment variables:")
        print("   - GITLAB_TOKEN (or CI_JOB_TOKEN)")
        print("   - CI_PROJECT_ID")
        print("   - XAI_API_KEY")
        sys.exit(1)

    print(f"🔍 Fetching MR #{mr_number} info...")
    mr_info = get_mr_info(mr_number)

    print(f"📥 Fetching MR #{mr_number} diff...")
    diff_text = get_mr_diff(mr_number)

    if not diff_text.strip():
        print("⚠️  No relevant files to review (only reviewing .kt, .java, .gradle, .xml)")
        sys.exit(0)

    print(f"🤖 Reviewing with Grok (grok-4-1-fast)...")
    review_text = review_with_grok(mr_number, diff_text, mr_info)

    print("💾 Saving report...")
    report_path = save_report(mr_number, review_text)

    if POST_COMMENT:
        print("💬 Posting comment to MR...")
        post_mr_comment(mr_number, report_path)

    print("✨ Done!")

if __name__ == '__main__':
    main()
