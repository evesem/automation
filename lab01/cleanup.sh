#!/bin/bash

# Check if directory argument is provided
if [ $# -lt 1 ]; then
    echo "Error: Please specify a directory."
    echo "Usage: ./cleanup.sh <directory> [extension1] [extension2] ..."
    exit 1
fi

DIRECTORY="$1"
shift

# Check if directory exists
if [ ! -d "$DIRECTORY" ]; then
    echo "Error: Directory '$DIRECTORY' does not exist."
    exit 1
fi

# If no extensions are provided, use .tmp by default
if [ $# -eq 0 ]; then
    EXTENSIONS=(".tmp")
else
    EXTENSIONS=("$@")
fi

deleted_count=0

# Delete files with specified extensions
for extension in "${EXTENSIONS[@]}"; do
    while IFS= read -r -d '' file; do
        rm "$file"
        if [ $? -eq 0 ]; then
            ((deleted_count++))
        fi
    done < <(find "$DIRECTORY" -type f -name "*$extension" -print0)
done

echo "Number of deleted files: $deleted_count"
