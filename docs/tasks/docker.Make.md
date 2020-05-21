# docker.Make

## Description
This task executes a make target from within a docker container. This task requires that there is a Makefile in the directory from where the task was called.

## Required Parameters

* docker
  * image
    * Name of the docker image that will be used to create the container that the make target will be run inside of.
  * version
    * Version of the docker image that will be used to create the container that the make target will be run inside of.
* target
  * Make target will be executed inside of the created container.

## Optional Parameters
* docker
  * shell
    * Shell that will be used in the docker container (`'bash'` by default).
  * workDir
    * Working directory that the task will use inside of the container (`'/project'` by default).
      * The directory that the task is called from will be mounted to this directory on the created container.
  * env
    * Environment variables that are set in the started container ([] by default)
  * volumes
    * This used to list any extra volumes you would like to mount on to the started container, using the syntax of the docker run `-v` option. ([] by default)
# Navigation
* [Home](../../README.md)
* [Task Documentation](README.md)
