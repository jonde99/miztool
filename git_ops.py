from git import Repo

def git_pull(repo_path):
    repo = Repo(repo_path)
    result = repo.remotes.origin.pull()
    return "\n".join(str(r) for r in result)


def git_status(repo_path):
    repo = Repo(repo_path)
    return repo.git.status()

def git_commit_push(repo_path, message):
    repo = Repo(repo_path)
    repo.git.add(A=True)
    if repo.is_dirty():
        repo.index.commit(message)
        repo.remotes.origin.push()
