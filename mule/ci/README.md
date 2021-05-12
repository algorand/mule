# muleci

This package is for code related to the muleci project.

## Archetypes
Archetypes are generic pipeline implementations for different stacks. They all implement [IArchetype](archetype/__init__.py) so that muleci knows how to perform pipeline operations. When implementing an archetype, you have the option to implement each action supported by the muleci cli (build, publish, deploy, etc)

* [docker](archetype/docker.py)
  * Used to generically build/publish/deploy any project with a Dockerfile in the root directory. It uses git commit hashes for versioning.
  * actions
    * deps
      * Installs the awscli and helm
    * build
      * builds docker image
    * publish
      * Ensures that there is an appropriate ECR repository, and pushes the built docker image there
    * deploy
      * Uses the [rest-api](../util/resources/charts/rest-api) helm chart to deploy the app to kubernetes. It uses either the currently configured k8s cluster, or will deployed to an eks cluster specified with `EKS_CLUSTER_NAME`.
    * undeploy
      * Deletes the specified helm release for this application.
* [npm](archetype/node.py)
  * This archetype is currently the same as the docker archetype, but it uses the package.json for versioning. It also depends on a Dockerfile.
  * actions
    * same as docker

    