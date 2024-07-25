#!/bin/bash

filename="filtered_url.txt"

if [ -f "$filename" ]; then
    > "$filename"
else
    touch "$filename"
fi