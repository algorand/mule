#!/bin/bash

if ! which pytest > /dev/null
then
    echo "$(tput setab 7)$(tput setaf 4)[INFO]$(tput sgr0) $(tput bold)pytest$(tput sgr0) is not present on the system..."
    exit 0
fi

FILES=$(git diff-index --cached --name-only HEAD 2> /dev/null | grep ".py\b")

if [ -n "$FILES" ]
then
    echo "$(tput setab 7)$(tput setaf 4)[INFO]$(tput sgr0) Running $(tput bold)pytest$(tput sgr0) pre-commit hook..."

    cd tests || exit
    pytest -v
    EXIT_CODE="$?"

    if [ $EXIT_CODE -eq 0 ]
    then
        echo "$(tput setab 7)$(tput setaf 2)[INFO]$(tput sgr0) Completed successfully."
    fi
fi

exit $EXIT_CODE

