#!/bin/bash

# Update prefix/suffix dictionary in json format from original tsv file. 
FILES=original_data/*.*
for file in $FILES
do
    
    filename=$(basename ${file})
    word_type=$(basename ${file%.*})
    
    # Call generate_prefix_suffix_dict.py
    echo "Converting ${filename}..."
    python3 generate_prefix_suffix_dict.py \
        ${file} \
        ${word_type} \
        "../${word_type}.json"
    
done