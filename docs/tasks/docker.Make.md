# docker.Make

## Description
This task executes a make target from within a docker container. This task requires that there is a Makefile in the directory that the task is called from.

## Required Parameters

* image
  * Name of the docker image that will be used to create the container that the make target will be run inside of.
* version
  * Version of the docker image that will be used to create the container that the make target will be run inside of.
* target
  * Make target will be executed inside of the created container.

## Optional Parameters
* workDir
  * Working directory that the task will use inside of the container. (`'/project'` by default)
    * The directory that the task is called from will be mounted to this directory on the created container.

# Navigation
* [Home](../../README.md)
* [Task Documentation](README.md)
