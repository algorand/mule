#!/bin/bash

echo "$(tput setaf 2)[INFO]$(tput sgr0) Adding pre-commit hooks to .gitconfig..."
git config --global --add hooks.pre-commit.mule "pycodestyle.sh"
git config --global --add hooks.pre-commit.mule "pytest.sh"

