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
    mkdir -p $project_path/data/keywords/others
    mkdir -p $project_path/data/sentences/others

else
    echo "Project name exists! Pick a new name or run keyword generator instead"
    exit
fi
