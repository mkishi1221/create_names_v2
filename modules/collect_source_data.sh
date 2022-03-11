#!/bin/bash

sentences=$1
keywords=$2

# Check if data with sentences exists
if [ "$sentences" == "exists" ]; then
    # Pour source texts into one file
    FILES=data/sentences/*.txt
    for f in $FILES
    do
    cat ${f} \
    >> tmp/user_sentences.tsv
    echo "" >> tmp/user_sentences.tsv
    done
else
    > tmp/user_sentences.tsv
fi

# Check if data with keywords exists
if [ "$keywords" == "exists" ]; then
    # Pour user provided keywords into one file
    FILES=data/keywords/*.txt
    for f in $FILES
    do
    cat ${f} \
    >> tmp/user_keywords.tsv
    echo "" >> tmp/user_keywords.tsv
    done
else
    > tmp/user_keywords.tsv
fi