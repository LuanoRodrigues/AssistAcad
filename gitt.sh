#!/bin/bash

# Define repository URL
repo_url="https://github.com/LuanoRodrigues/AssistAcad.git"

# Absolute path to the project directory
project_path="/C/Users/luano/Downloads/AcAssitant"

# Check if the project directory exists
if [ ! -d "$project_path" ]; then
    echo "Project directory not found: $project_path"
    exit 1
fi

# Navigate to the project directory
cd "$project_path" || exit 1

# Add all changes
git add .

# Commit changes with a default message
git commit -m "Auto commit"

# Push changes to the remote repository
git push origin master

# Check if the push was successful
if [ $? -eq 0 ]; then
    echo "Push successful"
else
    echo "Push failed"
fi
