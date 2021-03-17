# Change Log
All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](https://semver.org/).
This file uses change log convention from [Keep a CHANGELOG](https://keepachangelog.com/en/1.0.0/).

## 0.0.21 - 2021-3-17
### Added
* Support for base_name overrides in rest-api deployments. The old implementation prevented multiple apps on one domain.

## 0.0.0

This implements the first set of tasks we have developed for our ci process as well as the core functionality of our yaml parser. Documentation for these tasks are in docs/tasks

Tasks:
* [release.notes.GenerateReleaseNotes](../docs/tasks/release.notes.GenerateReleaseNotes.md)
* [docker.Make](../docs/tasks/docker.Make.md)
* [docker.Version](../docs/tasks/docker.Version.md)
* [docker.Shell](../docs/tasks/docker.Shell.md)
* [shell.Make](../docs/tasks/shell.Make.md)
* [shell.docker.Build](../docs/tasks/shell.docker.Build.md)
* [shell.docker.Ensure](../docs/tasks/shell.docker.Ensure.md)
