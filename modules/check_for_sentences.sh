#!/bin/bash

# Check if data with sentences exists
function check_for_sentences()
{
    if [ -n "$(ls -A data/sentences/*.txt 2>/dev/null)" ]; then
        # Pour source texts modification dates into one file
        sentences="exists"
        FILES=data/sentences/*.*
        for f in $FILES
        do
        ls -lh ${f} \
        >> ref/logs/source_data_log.tsv
        done
    else
        sentences="none"
    fi
    echo $sentences
}

sentences="$(check_for_sentences)"

echo $sentences