#!/bin/bash

if ! which pycodestyle > /dev/null
then
    echo "$(tput setab 7)$(tput setaf 4)[INFO]$(tput sgr0) $(tput bold)pycodestyle$(tput sgr0) is not present on the system..."
    exit 0
fi

FILES=$(git diff-index --cached --name-only HEAD 2> /dev/null | grep ".py\b")

if [ -n "$FILES" ]
then
    echo "$(tput setab 7)$(tput setaf 4)[INFO]$(tput sgr0) Running $(tput bold)pycodestyle$(tput sgr0) pre-commit hook..."

    for file in $FILES
    do
        pycodestyle "$file"

        if [ "$?" -eq 1 ]
        then
            # Note that pycodestyle's error messages are verbose enough that we don't need to have our own.
            EXIT_CODE=1
        fi
    done

    if [ $EXIT_CODE -eq 0 ]
    then
        echo "$(tput setab 7)$(tput setaf 2)[INFO]$(tput sgr0) Completed successfully."
    fi
fi

exit $EXIT_CODE

