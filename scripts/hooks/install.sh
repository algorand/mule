#!/bin/bash

echo "$(tput setaf 2)[INFO]$(tput sgr0) Adding local pre-commit hooks to .git/config..."
git config --local --add hooks.pre-commit.mule "pycodestyle.sh"
git config --local --add hooks.pre-commit.mule "pytest.sh"

