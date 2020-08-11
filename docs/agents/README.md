# Agents

## Description

`agents` are lists of objects that define an agent for running `mule` tasks.  The only type of agent currently supported is `docker`, but this will be expanded to include others in the future.

## Required Parameters

* dockerFilePath
  * Path to the Dockerfile to be used to build the image.
* image
  * Name of the docker image that will be used to create the container that the make target will run inside.
* version
  * Version of the docker image that will be used to create the container that the make target will run inside.

## Optional Parameters

* buildArgs
  * `docker` build arguments that are passed to the `docker build` command.
  * [Command substitution](https://www.gnu.org/software/bash/manual/html_node/Command-Substitution.html) is supported for build argument values.
* env
  * Environment variables that are set in the started container (`[]` by default).
* volumes
  * This used to list any extra volumes you would like to mount on to the started container, using the syntax of the docker run `-v` option (`[]` by default).
* shell
  * Shell that will be used in the docker container (`'bash'` by default).
* workDir
  * Working directory that the task will use inside of the container (`'/project'` by default).
      * The directory that the task is called from will be mounted to this directory on the created container.

# Navigation

* [Home](../../README.md)
* [Task Documentation](README.md)

