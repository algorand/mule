# docker.Shell

## Description

This task executes a shell command from within a docker container.  Please see our [agent documentation](agents/README.md) for more information on defining agents.

## Required Parameters

* agent
  * An existing image name or name of an agent defined in the `agents` block.

* command
  * Make target will be executed inside of the created container.

## Examples

The first example mandates the existence of an `agents` block because the `docker.Shell` task references it in its `agent` config.

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
  - task: docker.Shell
    agent: ubuntu
    command: cat /etc/*release

jobs:
  cat-release:
    tasks:
    - docker.Shell
```

The second example is a kind of shorthand as it references an existing image (either locally or on Docker Hub) in its `agent` config.

```
tasks:
  - task: docker.Shell
    command: cat /etc/*release
    agent: amd64/alpine:latest

jobs:
  cat-release:
    tasks:
    - docker.Shell
```

# Navigation

* [Home](../../README.md)
* [Task Documentation](README.md)

