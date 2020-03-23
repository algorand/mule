# shell.docker.Build

## Description
This task computes a version used to identify a docker image used for builds.

## Required Parameters

* buildContextPath
  * Directory used as the context path of the docker build.
* tags
  * Tags that need to be assigned to the created docker image.
* dockerFilePath
  * Relative path to the dockerfile used to create the docker image.
    * This must be within the path of the directory from where this task is called.

## Optional Parameters

* buildArgs
  * Build arguments that will be passed to the docker build process (`''` by default).

# Navigation
* [Home](../../README.md)
* [Task Documentation](README.md)
