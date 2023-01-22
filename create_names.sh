#!/bin/bash

project_id=$1

if [ -z "$project_id" ]
then
    printf "Enter project ID or press enter to escape: "
    read -r  project_id

    if [ -z "$project_id" ]
    then
        exit
    fi
fi

project_path="projects/$project_id"

if [ ! -d $project_path ]
then 
    echo "ERROR: Directory \"$project_id\" does not exist. Check the project name and try again."
    exit
fi

# Calculate time elapsed
date
start_time=`gdate +%s%3N`

# Create required folders
# Clear tmp files
rm -rf $project_path/tmp/name_generator/*
rm -rf $project_path/tmp/domain_checker
rm -rf $project_path/results/domains.xlsx
mkdir -p $project_path/tmp/logs
mkdir -p $project_path/tmp/name_generator
mkdir -p $project_path/results/

python3 name_generator/name_generator.py \
    $project_id

# Calculate time elapsed
end_time=`gdate +%s%3N`
min_elapsed=$(echo "scale=0; (${end_time}-${start_time})/1000/60" | bc )
sec_elapsed=$(echo "scale=3; ((${end_time}-${start_time})/1000)-(${min_elapsed}*60)" | bc )
echo "All files processed. Total: ${min_elapsed}min, ${sec_elapsed}sec." 
date
