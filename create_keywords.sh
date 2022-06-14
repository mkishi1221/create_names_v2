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

if [ ! -d $project_path ];
then
    printf "Project files with name \"$project_id\" not detected. Press Y to create new project files, press N to look for existing project or press enter to escape: "
    read -r  affirm

    if [[ $affirm == "Y" || $afirm == "y" ]];
    then
        mkdir -p $project_path/data/keywords/others
        mkdir -p $project_path/data/sentences/others

        echo "Project folders created: place relevant data in data folder and run script again."
        exit
    
    elif [[ $affirm == "N" || $afirm == "n" ]];
    then
        printf "Enter project ID or press enter to escape: "
        read -r  project_id
        project_path="projects/$project_id"

        if [ -z "$project_id" ]
        then
            exit
        elif [ ! -d $project_path ]
        then
            echo "Project files with name $project_id not found. Exiting script..."
        fi

    else
        exit
    fi
fi

# Calculate time elapsed
date
start_time=`gdate +%s%3N`

# Check if data with sentences exists
sentences="$(sh name_generator/modules/check_for_sentences.sh $project_id)"
# Check if data with keywords exists
keywords="$(sh name_generator/modules/check_for_keywords.sh $project_id)"

# Exit script if no sentences or keywords detected.
if [ "$sentences" == "exists" -a "$keywords" == "exists" ]; then
    echo "Running script with both sentences and keywords..."
elif [ "$sentences" == "exists"  -a "$keywords" == "none" ]; then
    echo "No keywords found. Running script with only sentences..."
elif [ "$sentences" == "none"  -a "$keywords" == "exists" ]; then
    echo "No sentences found. Running script with only keywords..."
elif [ "$keywords" == "none"  -a "$sentences" == "none" ]; then
    echo "No sentences and keywords detetcted! Please add source data in txt format to the \"data\" folder."
    exit
fi

# Clear tmp files
rm -rf $project_path/tmp/keyword_generator/*
rm -rf $project_path/tmp/name_generator/*
rm -rf $project_path/tmp/domain_checker/*
rm -rf $project_path/results/names.xlsx
rm -rf $project_path/results/domains.xlsx
mkdir -p $project_path/tmp/keyword_generator
mkdir -p $project_path/tmp/logs
mkdir -p $project_path/results/

# Collect source data into one tmp file each for sentences and for keywords
echo "Collect source data into tmp files..."
sh name_generator/modules/collect_source_data.sh $sentences $keywords $project_id

# Generate word list from source text
# Words to be sorted by POS, length and other factors in the future to accomodate more complex name-generating algorithms.
echo "Creating word list..."
python3 name_generator/keyword_generator.py \
    $project_id

# Calculate time elapsed
end_time=`gdate +%s%3N`
min_elapsed=$(echo "scale=0; (${end_time}-${start_time})/1000/60" | bc )
sec_elapsed=$(echo "scale=3; ((${end_time}-${start_time})/1000)-(${min_elapsed}*60)" | bc )
echo "All files processed. Total: ${min_elapsed}min, ${sec_elapsed}sec." 
date
