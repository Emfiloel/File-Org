# Version Transition Process

This document outlines the process for transitioning between major versions of File Organizer, ensuring that the latest version is always public while previous versions are archived privately.

## Repository Strategy

- **Public Repository (File-Org):** Contains ONLY the current version
- **Private Repository (File-Org-Archive):** Contains all previous versions

## When to Transition

Transition to a new version when:
- Major feature additions are complete
- All tests pass
- Documentation is updated
- Ready for public distribution

## Transition Steps

### Step 1: Prepare Archive Repository

```bash
# Create local archive directory (if not exists)
cd /path/to/projects
mkdir -p file-organizer-archive
cd file-organizer-archive
git init  # Only if new archive repo

# Copy current version to archive
cp -r /path/to/file-organizer/v{X}.{Y}/ .
cp /path/to/file-organizer/LICENSE .
cp /path/to/file-organizer/.gitignore .

# Commit to archive
git add .
git commit -m "Archive v{X}.{Y}

This is the archived release of File Organizer v{X}.{Y}.
The current development version is maintained in the public File-Org repository.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

# Push to private GitHub repository
git remote add origin https://github.com/Emfiloel/File-Org-Archive.git  # Only first time
git push -u origin main
```

### Step 2: Update Public Repository

```bash
cd /path/to/file-organizer

# Remove old version from public repo
git rm -r v{X}.{Y}/

# Rename dev version to release version
git mv v{X}.{Y+1}-dev/ v{X}.{Y+1}/
```

### Step 3: Update Documentation

**Update README.md:**
- Change version numbers (v{X}.{Y} → v{X}.{Y+1})
- Update test counts
- Update paths in code examples
- Update "Last Updated" date

**Update CI Workflows:**
```bash
# Replace version in all workflow files
sed -i 's/v{X}\.{Y}/v{X}.{Y+1}/g' .github/workflows/*.yml
```

**Files to update:**
- `.github/workflows/ci.yml`
- `.github/workflows/code-quality.yml`
- `.github/workflows/pr-checks.yml`
- `.github/workflows/release.yml`

### Step 4: Commit and Push

```bash
git add .
git commit -m "feat(v{X}.{Y+1}): release v{X}.{Y+1} and archive v{X}.{Y}

Changes:
- Archived v{X}.{Y} to private repository
- Promoted v{X}.{Y+1}-dev to v{X}.{Y+1}
- Updated all documentation and CI workflows
- Updated README with new version info

v{X}.{Y} is now available in File-Org-Archive (private)
v{X}.{Y+1} is now the current public version

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

git push origin master
```

## Example: v7.0 → v7.1 Transition

### What Was Done

1. **Created archive repository:**
   - Created `/l/Templates/Projects/file-organizer-archive/`
   - Copied v7.0/ to archive
   - Committed and pushed to private `File-Org-Archive` repo

2. **Updated public repository:**
   - Removed v7.0/ with `git rm -r v7.0/`
   - Renamed v7.1-dev/ to v7.1/ with `git mv v7.1-dev/ v7.1/`

3. **Updated documentation:**
   - Updated README.md with v7.1 info
   - Updated test count (67 → 90)
   - Changed all v7.0 references to v7.1
   - Added archive repository link

4. **Updated CI workflows:**
   - Changed `pip install -r v7.0/requirements.txt` to `v7.1/requirements.txt`
   - Changed `cd v7.0` to `cd v7.1` in all workflows
   - Updated 4 workflow files

5. **Committed changes:**
   - Single commit with all changes
   - Pushed to GitHub

## Checklist

Use this checklist for each transition:

- [ ] All new features complete and tested
- [ ] All tests passing locally
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Archive repository prepared locally
- [ ] Old version copied to archive
- [ ] Archive committed and pushed to private repo
- [ ] Old version removed from public repo
- [ ] Dev version renamed to release version
- [ ] README.md updated
- [ ] All 4 CI workflows updated
- [ ] Changes committed with descriptive message
- [ ] Pushed to GitHub
- [ ] Verified public repo shows only new version
- [ ] Verified archive repo contains old version

## Important Notes

1. **Privacy:** The archive repository must ALWAYS be private to protect historical versions from public access.

2. **Data Protection:** Before ANY commit, verify .gitignore protects all user data:
   - `**/.file_organizer_data/*.db`
   - `**/.file_organizer_data/*.log`
   - `**/.file_organizer_data/operations.jsonl`
   - Never commit user paths, filenames, or personal data

3. **Version Numbering:**
   - Development versions: `v{X}.{Y}-dev`
   - Release versions: `v{X}.{Y}`
   - Major features: Increment Y (v7.1 → v7.2)
   - Major rewrites: Increment X (v7.9 → v8.0)

4. **Archive Only After Release:** Don't archive until the new version is stable and ready for public distribution.

5. **Single Source of Truth:** The public repository should ONLY contain the current version. Previous versions live in the private archive.

## Future Version Roadmap

- **v7.2:** [Planned features]
- **v7.3:** [Planned features]
- **v8.0:** [Major rewrite/redesign]

---

**Process Created:** December 26, 2025
**Last Updated:** December 26, 2025
