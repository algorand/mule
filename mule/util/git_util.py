import os
import git

def getLastTag():
    cwd = os.getcwd()
    repo = git.Repo(cwd)
    return repo.tags[-1]

def getCommitsSinceTag(tag):
    cwd = os.getcwd()
    repo = git.Repo(cwd)
    return repo.iter_commits(rev=f"{tag}..HEAD")

def getCommitsSinceLastTag():
    last_tag = getLastTag()
    return getCommitsSinceTag(last_tag)

def getHeadCommitHash():
    cwd = os.getcwd()
    repo = git.Repo(cwd)
    return repo.head.object.hexsha
