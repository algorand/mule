# shell.docker.Ensure

## Description
This task computes a version used to identify a docker image used for builds.

## Required Parameters

* image
  * Name of the docker image that needs to be made available.
* version
  * Image of the docker image that needs to be made available.
* dockerFilePath
  * Relative path to the dockerfile used to create the docker image if it is not available.
    * This must be within the path of the directory this task is called in.
* arch
  * CPU architecture of the docker image that needs to be made available.

## Optional Parameters

* buildContextPath
  * Directory used as the context path of a docker build. (`'.'` by default)

# Navigation
* [Home](../../README.md)
* [Task Documentation](README.md)
