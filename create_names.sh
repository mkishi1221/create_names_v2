#!/bin/bash

# Calculate time elapsed
date
start_time=`gdate +%s%3N`

# Create required folders
mkdir -p tmp
mkdir -p ref/logs
mkdir -p results/

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

# Compare contents of current and previous log files
# If source data has changed, recompile source data, dictionary and generated name lists.
if [[ "$(cat ref/logs/prev_source_data_log.tsv)" == "$(cat ref/logs/source_data_log.tsv)" && "$(cat ref/logs/prev_script_log.tsv)" == "$(cat ref/logs/script_log.tsv)" ]];then
    echo "Source data or script unchanged."

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
        results/keywords.xlsx
    
    cat ref/logs/source_data_log.tsv > ref/logs/prev_source_data_log.tsv
    cat ref/logs/script_log.tsv > ref/logs/prev_script_log.tsv
fi

# Calculate time elapsed
end_time=`gdate +%s%3N`
min_elapsed=$(echo "scale=0; (${end_time}-${start_time})/1000/60" | bc )
sec_elapsed=$(echo "scale=3; ((${end_time}-${start_time})/1000)-(${min_elapsed}*60)" | bc )
echo "All files processed. Total: ${min_elapsed}min, ${sec_elapsed}sec." 
date
