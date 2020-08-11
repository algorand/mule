# docker.Make

## Description

This task executes a make target from within a docker container. This task requires that there is a Makefile in the directory from where the task was called.

Please see our [agent documentation](agents/README.md) for more information on defining agents.

## Required Parameters

* agent
  * The name of an agent defined in the `agents` block.

* target
  * Make target will be executed inside of the created container.

## Examples

```
agents:
  - name: ubuntu
    dockerFilePath: Dockerfile.test
    image: algorand/go-algorand-ci-linux-ubuntu
    version: README.md
    buildArgs:
      - GOLANG_VERSION=`./get_golang_version.sh`
      - PWD=`pwd`
      - Z=ZED
    env:
      - A=${A}
      - B=${B}
    workDir: $HOME/projects/go-algorand

tasks:
  - task: docker.Make
    agent: ubuntu
    target: build

jobs:
  build:
    tasks:
    - docker.Make
```

# Navigation

* [Home](../../README.md)
* [Task Documentation](README.md)

