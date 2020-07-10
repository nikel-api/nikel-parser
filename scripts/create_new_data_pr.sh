#!/bin/bash
working_dir=$PROJECT_DIR/nikel-parser
cd $PROJECT_DIR/nikel-parser

today=`date +'%m_%d_%Y_%H_%M_%S'`
branch_name="update_dataset_$today"

# New branch for changes
git checkout -b "$branch_name"


# Only commit the JSON data & pickles
git add data/* pickles/*

# Commit and push to upstream
# Commit message will also be title of the PR created
git commit -m "updates/dataset_$today"
git push --set-upstream origin "$branch_name"

# Create new PR
hub pull-request --no-edit
