#!/bin/bash

# Create log files if not exist
touch projects/project_x/tmp/logs/prev_source_data_log.tsv
touch projects/project_x/tmp/logs/prev_script_log.tsv

# Reset current log files to be blank
> projects/project_x/tmp/logs/source_data_log.tsv
> projects/project_x/tmp/logs/script_log.tsv

# Pour script file modification dates into one file
for f in *.py *.sh *.xlsx
do
ls -lh ${f} \
>> projects/project_x/tmp/logs/script_log.tsv
done

FILES=name_generator/modules/*.*
for f in $FILES
do
ls -lh ${f} \
>> projects/project_x/tmp/logs/script_log.tsv
done

FILES=name_generator/classes/*.*
for f in $FILES
do
ls -lh ${f} \
>> projects/project_x/tmp/logs/script_log.tsv
done