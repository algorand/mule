from github import Github
from mule.util import git_util
from mule.util import file_util

def createGithubReleaseForCurrentRepo(patToken, repoFullName, commitHash, version, notes, assetFolderPath):
    github_client = Github(patToken)
    repository = github_client.get_repo(repoFullName)
    release = repository.create_git_release(version, version, notes, draft=True, target_commitish=commitHash)
    assetPaths = file_util.getFilesInFolder(assetFolderPath)
    for assetPath in assetPaths:
        release.upload_asset(assetPath)
