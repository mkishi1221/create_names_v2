#!/bin/bash

# Check if data with keywords exists
if [ -n "$(ls -A projects/$1/data/keywords/*.txt 2>/dev/null)" ]; then
    keywords="exists"
else
    keywords="none"
fi

echo ${keywords}