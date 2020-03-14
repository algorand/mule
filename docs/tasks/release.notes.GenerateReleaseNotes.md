# release.notes.GenerateReleaseNotes

## Description
This task generates a draft of release notes for a new version using the git commit messages of every commit that has been made since the previous tagged release. It will upload every file in designated assets folder (`assets` by default) as assets to the release.

## Required Parameters
* releaseVersion
  * Version of the new release. This value is also used as a tag for the HEAD commit of the branch this process is being run from.
* githubPatToken
  * Github PAT token with access to create releases for the desired repository
* githubRepoFullName
  * Full name of the github repository (for example, `algorand/go-algorand`)

## Optional Parameters
* assetFolderPath
  * Path to folder where all of the release assets are stored (`assets` by default)

# Navigation
* [Home](../../README.md)
* [Task Documentation](README.md)
