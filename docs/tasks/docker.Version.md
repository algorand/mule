# docker.Version

## Description
This task computes a version used to identify a docker image used for builds.

## Required Parameters

* arch
  * Target cpu architecture of the docker image.
* configFilePath
  * Config file who's hash will be used to identify the version of the docker image. This will generally be a script run to configure the docker image appropriately for a build.

## Outputs
* version
  * Version string computed by this task.

# Navigation
* [Home](../../README.md)
* [Task Documentation](README.md)
