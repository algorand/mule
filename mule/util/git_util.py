import os
import git

cwd = os.getcwd()
repo = git.Repo(cwd, search_parent_directories=True)

def getLastTag():
    return repo.tags[-1]

def getCommitsSinceTag(tag):
    return repo.iter_commits(rev=f"{tag}..HEAD")

def getCommitsSinceLastTag():
    last_tag = getLastTag()
    return getCommitsSinceTag(last_tag)

def getHeadCommitHash():
    return repo.head.object.hexsha
