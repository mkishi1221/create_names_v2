#!/bin/bash

# Check if data with keywords exists
if [ -n "$(ls -A data/keywords/*.txt 2>/dev/null)" ]; then
    # Pour source texts modification dates into one file
    keywords="exists"
    FILES=data/keywords/*.*
    for f in $FILES
    do
    ls -lh ${f} \
    >> ref/logs/source_data_log.tsv
    done
else
    keywords="none"
fi

echo ${keywords}