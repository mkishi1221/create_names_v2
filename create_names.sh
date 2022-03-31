#!/bin/bash

# Calculate time elapsed
date
start_time=`gdate +%s%3N`

# Create required folders
mkdir -p tmp
mkdir -p ref/logs
mkdir -p results/

python3 name_generator.py \
    results/keywords.xlsx \
    data/name_styles/name_style_list.xlsx \
    results/names.json

# Calculate time elapsed
end_time=`gdate +%s%3N`
min_elapsed=$(echo "scale=0; (${end_time}-${start_time})/1000/60" | bc )
sec_elapsed=$(echo "scale=3; ((${end_time}-${start_time})/1000)-(${min_elapsed}*60)" | bc )
echo "All files processed. Total: ${min_elapsed}min, ${sec_elapsed}sec." 
date
