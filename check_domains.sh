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
mkdir -p $project_path/tmp/domain_checker
mkdir -p $project_path/results/

export SOCKS=ihgosdbs-rotate:a6au825lb0n3@p.webshare.io:80

python3 name_generator/domain_checker.py \
    $project_id \
    500

# Calculate time elapsed
end_time=`gdate +%s%3N`
min_elapsed=$(echo "scale=0; (${end_time}-${start_time})/1000/60" | bc )
sec_elapsed=$(echo "scale=3; ((${end_time}-${start_time})/1000)-(${min_elapsed}*60)" | bc )
echo "All files processed. Total: ${min_elapsed}min, ${sec_elapsed}sec." 
date