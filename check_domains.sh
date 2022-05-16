#!/bin/bash

# Calculate time elapsed
date
start_time=`gdate +%s%3N`

# Create required folders
mkdir -p tmp/logs
mkdir -p tmp/domain_checker
mkdir -p results/

python3 domain_checker.py \
    tmp/name_generator/names_shortlist.json \
    50 \
    tmp/domain_checker/domains.json

# Calculate time elapsed
end_time=`gdate +%s%3N`
min_elapsed=$(echo "scale=0; (${end_time}-${start_time})/1000/60" | bc )
sec_elapsed=$(echo "scale=3; ((${end_time}-${start_time})/1000)-(${min_elapsed}*60)" | bc )
echo "All files processed. Total: ${min_elapsed}min, ${sec_elapsed}sec." 
date