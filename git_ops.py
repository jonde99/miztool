from git import Repo

from git import Repo

def git_pull(repo_path):
    repo = Repo(repo_path)

    branch = repo.active_branch.name
    before = repo.head.commit

    results = repo.remotes.origin.pull()

    after = repo.head.commit

    # No changes
    if before.hexsha == after.hexsha:
        return f"Branch: {branch}\nAlready up to date."

    # Commits pulled
    commits = list(repo.iter_commits(f"{before.hexsha}..{after.hexsha}"))

    # Aggregate stats
    files = insertions = deletions = 0
    for c in commits:
        s = c.stats.total
        files += s.get("files", 0)
        insertions += s.get("insertions", 0)
        deletions += s.get("deletions", 0)

    return (
        f"Branch: {branch}\n"
        f"Commits pulled: {len(commits)}\n"
        f"Files changed: {files}\n"
        f"Insertions: {insertions}\n"
        f"Deletions: {deletions}"
    )


def git_commit(repo_path, message):
    repo = Repo(repo_path)
    repo.git.add(A=True)

    if not repo.is_dirty():
        return "No changes to commit."

    commit = repo.index.commit(message)

    # Diff stats against parent
    stats = commit.stats.total

    files = stats.get("files", 0)
    insertions = stats.get("insertions", 0)
    deletions = stats.get("deletions", 0)

    return (
        f"Commit: {commit.hexsha[:8]}\n"
        f"Message: {commit.message.strip()}\n"
        f"Files changed: {files}\n"
        f"Insertions: {insertions}\n"
        f"Deletions: {deletions}"
    )

def git_push(repo_path):
    repo = Repo(repo_path)
    results = repo.remotes.origin.push()

    lines = []
    for r in results:
        local = r.local_ref.name if r.local_ref else "unknown"
        remote = r.remote_ref.name if r.remote_ref else "unknown"
        lines.append(
            f"{local} -> {remote} : {r.summary}"
        )

    return "\n".join(lines) or "Nothing to push."


def git_status(repo_path):
    repo = Repo(repo_path)
    return repo.git.status()


