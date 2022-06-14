#!/bin/bash

sentences=$1
keywords=$2
project_id=$3

project_path=projects/$project_id

# Check if data with sentences exists
if [ "$sentences" == "exists" ]; then
    # Pour source texts into one file
    FILES=$project_path/data/sentences/*.txt
    for f in $FILES
    do
    cat ${f} \
    >> ${project_path}/tmp/keyword_generator/${project_id}_user_sentences.tsv
    echo "" >> ${project_path}/tmp/keyword_generator/${project_id}_user_sentences.tsv
    done
else
    > $project_path/tmp/keyword_generator/${project_id}_user_sentences.tsv
fi

# Check if data with keywords exists
if [ "$keywords" == "exists" ]; then
    # Pour user provided keywords into one file
    FILES=$project_path/data/keywords/*.txt
    for f in $FILES
    do
    cat ${f} \
    >> ${project_path}/tmp/keyword_generator/${project_id}_user_keywords.tsv
    echo "" >> ${project_path}/tmp/keyword_generator/${project_id}_user_keywords.tsv
    done
else
    > ${project_path}/tmp/keyword_generator/${project_id}_user_keywords.tsv
fi