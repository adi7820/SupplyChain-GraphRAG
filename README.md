# SupplyChain-GraphRAG

A GraphRAG (Knowledge Graph + Retrieval-Augmented Generation) system tailored for supply chain resilience, multi-tier dependency mapping, and disruption propagation analysis.

---

## 🚀 GitHub Actions & Workflow Automation

This repository is configured with automated PR creation (**Option A**):

### Automated Pull Request Workflow
Whenever a branch following the naming conventions below is pushed to GitHub, an automated workflow (`.github/workflows/auto-pr.yml`) opens a Pull Request to `main`:

- `feature/**` (e.g. `feature/graph-schema`, `feature/neo4j-connector`)
- `fix/**` (e.g. `fix/api-cors-issue`)
- `chore/**` (e.g. `chore/update-deps`)

### Automated PR Code Review Comments
Whenever a Pull Request is opened or updated, the **Automated PR Code Reviewer** (`.github/workflows/pr-review.yml`) triggers:
1. **Diff Extraction**: Computes the exact code diff targeting `main`.
2. **Gemini Code Review**: If `GEMINI_API_KEY` is configured in repository secrets, Google Gemini (`gemini-1.5-flash`) reviews the diff for architecture, potential bugs, security concerns, and actionable recommendations.
3. **Automated PR Comment**: Posts the structured review directly as a comment on the Pull Request.

> [!TIP]
> **Enable Gemini AI Code Reviews**:
> 1. In your GitHub repository, go to **Settings** > **Secrets and variables** > **Actions**.
> 2. Click **New repository secret**.
> 3. Name: `GEMINI_API_KEY`, Value: `<Your Google Gemini API Key>`.
> 4. Click **Add secret**. Future PRs will automatically receive full Gemini AI code review comments!

### Workflow Behavior
1. **Deduplication**: Checks if an open PR already exists for the head branch to prevent duplicates.
2. **Auto Title Generation**: Converts the branch slug into a clear title (e.g. `feature/vector-search` → `[feature] Vector Search`).
3. **Commit Summary**: Automatically lists recent commits in the PR body.

### Required GitHub Settings
To allow GitHub Actions to open PRs automatically on your repository:
1. Go to **Settings** > **Actions** > **General**.
2. Scroll to **Workflow permissions**.
3. Select **Read and write permissions**.
4. Check **Allow GitHub Actions to create and approve pull requests**.
5. Click **Save**.

---

## 🛠️ Branching Strategy

```
main (Production / Stable)
  ▲
  │ (Automated PR via GitHub Action)
  │
feature/*, fix/*, chore/* (Working Branches)
```

1. Create and switch to a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Commit your changes:
   ```bash
   git add .
   git commit -m "feat: your change description"
   ```
3. Push to GitHub:
   ```bash
   git push -u origin feature/your-feature-name
   ```
4. GitHub Actions will automatically detect the push and open a Pull Request targeting `main`.