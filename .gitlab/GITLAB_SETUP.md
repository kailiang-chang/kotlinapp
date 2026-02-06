# GitLab MR Review Setup Guide

Complete setup instructions for Grok-powered merge request reviews in GitLab.

## Prerequisites

1. GitLab project (gitlab.com or self-hosted)
2. xAI API key (for Grok)
3. GitLab personal access token (or use built-in CI_JOB_TOKEN)

## Setup Steps

### 1. Add CI/CD Variables

Go to **Settings > CI/CD > Variables** and add:

| Variable | Value | Type | Flags |
|----------|-------|------|-------|
| `XAI_API_KEY` | Your xAI (Grok) API key | Variable | Masked, Protected |
| `GITLAB_TOKEN` | Personal access token with `api` scope | Variable | Masked, Protected |

**Note:**
- Get your xAI API key from https://console.x.ai/
- You can use `CI_JOB_TOKEN` instead of `GITLAB_TOKEN`, but it has limited permissions. A personal access token is recommended for posting comments.

### 2. Copy Files to Your Repo

Copy these files to your GitLab repository:

```bash
# Create directory structure
mkdir -p .gitlab/scripts

# Copy the Python script
cp review_mr.py .gitlab/scripts/
cp requirements.txt .gitlab/scripts/

# Copy GitLab CI config (rename to .gitlab-ci.yml if this is your only pipeline)
cp .gitlab-ci-mr-review.yml .gitlab-ci.yml

# Make script executable
chmod +x .gitlab/scripts/review_mr.py
```

### 3. Commit and Push

```bash
git add .gitlab .gitlab-ci.yml
git commit -m "Add Claude MR review integration"
git push
```

## Usage

### Method 1: GitLab Web UI (Easiest)

1. Go to **CI/CD > Pipelines**
2. Click **Run pipeline**
3. Select branch: `main` or `master`
4. Add variables:
   - `MR_NUMBER`: `1` (the MR number to review)
   - `POST_COMMENT`: `true` (optional, to post comment on MR)
5. Click **Run pipeline**
6. Wait for completion
7. Download artifact from pipeline page

### Method 2: glab CLI

```bash
# Install glab if you haven't
# macOS: brew install glab
# Linux: https://gitlab.com/gitlab-org/cli#installation

# Trigger review for MR #1 without posting comment
glab ci run --branch=main --variable MR_NUMBER=1 --variable POST_COMMENT=false

# Wait for completion, then download artifact
glab ci artifact --job review-mr

# Read the report
cat reports/mr-1-review.md
```

### Method 3: GitLab API

```bash
# Set your variables
PROJECT_ID="your-project-id"
GITLAB_TOKEN="your-token"
MR_NUMBER=1

# Trigger pipeline
curl -X POST "https://gitlab.com/api/v4/projects/${PROJECT_ID}/pipeline" \
  --header "PRIVATE-TOKEN: ${GITLAB_TOKEN}" \
  --data "ref=main&variables[MR_NUMBER]=${MR_NUMBER}&variables[POST_COMMENT]=false"

# Get pipeline ID from response, then download artifacts
PIPELINE_ID="<from-response>"
curl --location --output artifacts.zip \
  --header "PRIVATE-TOKEN: ${GITLAB_TOKEN}" \
  "https://gitlab.com/api/v4/projects/${PROJECT_ID}/pipelines/${PIPELINE_ID}/jobs/artifacts/download"

# Unzip and read
unzip artifacts.zip
cat reports/mr-1-review.md
```

## Cost Optimization

The script uses **Grok 4.1 Fast** by default for cost savings.

To change the model, edit `.gitlab/scripts/review_mr.py` line ~90:

```python
# Current (grok-4-1-fast - fast and cost-effective)
model="grok-4-1-fast",

# Or use Grok 2 (more comprehensive reasoning)
model="grok-2-1212",
```

### File Filtering

Only these file types are reviewed (to save costs):
- `**/*.kt` - Kotlin
- `**/*.java` - Java
- `**/*.gradle` - Gradle
- `**/*.xml` - Android XML

To modify, edit the `should_review_file()` function in `review_mr.py`.

## Automatic Reviews (Optional)

To enable automatic reviews on every MR with code changes, uncomment the `auto-review-mr` job in `.gitlab-ci.yml`.

**Warning:** This will consume API credits on every MR. Use with caution.

## Troubleshooting

### "Missing required environment variables"

Ensure `XAI_API_KEY` and `GITLAB_TOKEN` are set in CI/CD Variables (Settings > CI/CD > Variables).

### "404 Not Found" when fetching MR

- Check that `MR_NUMBER` is correct
- Verify `GITLAB_TOKEN` has `api` scope
- For self-hosted GitLab, ensure `CI_API_V4_URL` is set correctly

### "Permission denied" when posting comments

The token needs write access to merge requests. Use a personal access token with `api` scope instead of `CI_JOB_TOKEN`.

### Script execution fails

Verify the script is executable:
```bash
chmod +x .gitlab/scripts/review_mr.py
```

## Comparison with GitHub Action

| Feature | GitHub Action | GitLab Integration |
|---------|--------------|-------------------|
| Setup | Pre-built action | Custom script |
| Complexity | Low | Medium |
| Tool restrictions | `--allowedTools` | Python script control |
| Artifacts | Built-in | Built-in |
| Comments | Built-in | API calls |
| Maintenance | Anthropic | You |

## Support

For issues with:
- **Grok API**: https://docs.x.ai/
- **GitLab CI/CD**: https://docs.gitlab.com/ee/ci/
- **This integration**: Open an issue in your repository
