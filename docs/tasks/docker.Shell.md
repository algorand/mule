# docker.Shell

## Description
This task executes a shell command from within a docker container.

## Required Parameters

* docker
  * image
    * Name of the docker image that will be used to create the container that the command will be run inside of.
  * version
    * Version of the docker image that will be used to create the container that the command will be run inside of.
* command
  * Shell command that will be executed inside of the created container.

## Optional Parameters
* docker
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
