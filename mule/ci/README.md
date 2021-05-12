# muleci

This package is for code related to the muleci project.

## Archetypes
Archetypes are generic pipeline implementations for different stacks. They all implement [IArchetype](archetype/__init__.py) so that muleci knows how to perform pipeline operations. When implementing an archetype, you have the option to implement each action supported by the muleci cli (build, publish, deploy, etc)

* [docker](archetype/docker.py)
    * Used to generically build/publish/deploy any project with a Dockerfile in the root directory. It uses git commit hashes for versioning.
* [npm](archetype/node.py)
    * This archetype is currently the same as the docker archetype, but it uses the package.json for versioning. It also depends on a Dockerfile.
    