#!/bin/bash

# Check if data with sentences exists
if [ -n "$(ls -A projects/$1/data/sentences/*.txt 2>/dev/null)" ]; then
    sentences="exists"
else
    sentences="none"
fi

echo ${sentences}