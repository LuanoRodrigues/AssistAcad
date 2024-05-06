#!/bin/bash

# Change to the project directory
cd "/c/Users/luano/Downloads/AcAssitant" || exit

# Add all changes to git
git add .

# Commit the changes with a message
echo "Enter commit message: "
read -r commit_message
git commit -m "$commit_message"

# Push the changes to the remote repository
git push origin main

echo "Changes pushed to GitHub."
