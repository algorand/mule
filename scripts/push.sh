#!/usr/bin/env bash

set -ex

VERSION=$1

if [[ -z $VERSION ]]
then
    VERSION=$(python3 setup.py --version)
fi

# Push to pypi.
python3 setup.py bdist_wheel
twine upload "dist/mulecli-$VERSION-py3-none-any.whl"

# Give the pypi repo a few seconds to update after the file is uploaded.
sleep 10

# Push to docker hub for pipelines.
docker build -t algorand/mule:latest -t "algorand/mule:$VERSION" . --no-cache
docker push algorand/mule:latest
docker push "algorand/mule:$VERSION"

