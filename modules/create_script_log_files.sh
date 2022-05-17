#!/bin/bash

# Create log files if not exist
touch tmp/logs/prev_source_data_log.tsv
touch tmp/logs/prev_script_log.tsv

# Reset current log files to be blank
> tmp/logs/source_data_log.tsv
> tmp/logs/script_log.tsv

# Pour script file modification dates into one file
for f in *.py *.sh *.xlsx
do
ls -lh ${f} \
>> tmp/logs/script_log.tsv
done

FILES=modules/*.*
for f in $FILES
do
ls -lh ${f} \
>> tmp/logs/script_log.tsv
done

FILES=classes/*.*
for f in $FILES
do
ls -lh ${f} \
>> tmp/logs/script_log.tsv
done