#/usr/bin/env bash
# shellcheck disable=2035

# https://www.gnu.org/software/grep/manual/html_node/Character-Classes-and-Bracket-Expressions.html
SELECTED_FILE="[[:graph:]]*.yaml"
FIELDS="--file --list-agents --list-env --list-jobs --list-tasks --recipe --verbose --version"

_mule_completion() {
    local curr_arg="${COMP_WORDS[COMP_CWORD]}"
    local last_arg="${COMP_WORDS[COMP_CWORD-1]}"
    local jobs

    if [[ "$last_arg" =~ -f|--file ]]
    then
        if stat -t *.yaml > /dev/null 2>&1
        then
            COMPREPLY=($(compgen -W "$(ls *.yaml)" "$curr_arg"))
        fi
    elif [[ "$curr_arg" =~ "--" ]]
    then
        COMPREPLY=($(compgen -W "$FIELDS" -- "$curr_arg" ))
    elif [ "$last_arg" = "--list-env" ]
    then
        # If `--list-env` has been selected, `$last_arg` will NOT contain the filename we need
        # to look up the jobs.  Instead, we'll (probably) find it in the `$COMP_WORDS` array.
        for item in "${COMP_WORDS[@]}"
        do
            if [[ "$item" =~ $SELECTED_FILE ]]
            then
                jobs=$(mule -f "$item" --list-jobs 2> /dev/null)
                break
            fi
        done
        COMPREPLY=($(compgen -W "$jobs" "$curr_arg"))
    elif [[ "$last_arg" =~ $SELECTED_FILE ]]
    then
        jobs=$(mule -f "$last_arg" --list-jobs 2> /dev/null)
        COMPREPLY=($(compgen -W "$jobs" "$curr_arg"))
    fi
}

complete -F _mule_completion mule

