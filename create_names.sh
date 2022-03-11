#!/bin/bash

# Calculate time elapsed
date
start_time=`gdate +%s%3N`

# Create required folders
mkdir -p tmp
mkdir -p ref/logs
mkdir -p results

# Set absolute imports
sh init_env.sh

# Check if testing files are still in the folders and restore data if nessesary
sh modules/check_for_testing_files.sh

# Load database credentials
sh modules/load_mongo_creds.sh

# Create script log files
sh modules/create_script_log_files.sh

# Check if data with sentences exists
sentences="$(sh modules/check_for_sentences.sh)"
# Check if data with keywords exists
keywords="$(sh modules/check_for_keywords.sh)"

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
else echo "Error: returned sentence and keyword availability indictor values not valid"
    exit
fi

# Run blacklist / whitelist generator if files exist in results folder
if [ -n "$(ls -A results/*.xlsx 2>/dev/null)" ]; then
    echo "Files found in results folder: running black/grey/white-list generator"
    python3 preference_generator.py \
        results/
else
    echo "Results folder is empty: skipping black/grey/white-list generator"
fi

# Compare contents of current and previous log files
# If source data has changed, recompile source data, dictionary and generated name lists.
if [[ "$(cat ref/logs/prev_source_data_log.tsv)" == "$(cat ref/logs/source_data_log.tsv)" && "$(cat ref/logs/prev_script_log.tsv)" == "$(cat ref/logs/script_log.tsv)" ]];then
    echo "Source data or script unchanged. Moving on to domain availability check..."

else
    echo "Source data or script changed. Recompiling source data..."
    # Clear tmp files
    rm -r tmp/*

    # Collect source data into one tmp file each for sentences and for keywords
    echo "Collect source data into tmp files..."
    sh modules/collect_source_data.sh ${sentences} ${keywords}

    # Generate word list from source text
    # Words to be sorted by POS, length and other factors in the future to accomodate more complex name-generating algorithms.
    echo "Creating word list..."
    python3 keyword_generator.py \
        tmp/user_sentences.tsv \
        tmp/user_keywords.tsv \
        tmp/keywords.json

    # Generate names
    echo "Initiating name generator script..."
    python3 name_generator.py \
        tmp/keywords.json \
        tmp/potential_names.json
    
    cat ref/logs/source_data_log.tsv > ref/logs/prev_source_data_log.tsv
    cat ref/logs/script_log.tsv > ref/logs/prev_script_log.tsv
fi

# Check domains 
# To make sure we don't overuse the API, the loop breaks after finding 10 available domains. You can change this limit by changing the "limit" variable defined below.
echo "Choosing names and initiating domain availability check..."
echo ""
dt=$(gdate '+%Y%m%d_%H%M%S')
limit=50
python3 domain_checker.py \
    tmp/potential_names.json \
    results/names_${dt}.xlsx \
    ${limit}

# Calculate time elapsed
end_time=`gdate +%s%3N`
min_elapsed=$(echo "scale=0; (${end_time}-${start_time})/1000/60" | bc )
sec_elapsed=$(echo "scale=3; ((${end_time}-${start_time})/1000)-(${min_elapsed}*60)" | bc )
echo "All files processed. Total: ${min_elapsed}min, ${sec_elapsed}sec." 
date
