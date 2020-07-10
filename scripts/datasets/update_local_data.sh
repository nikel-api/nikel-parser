#!/bin/bash

# ** Assumes $PROJECT_DIR is set to the directory where nikel-parser is cloned
cd $PROJECT_DIR/nikel-parser/data_parser

# Get latest changes
git checkout master
git pull

# Choose which parsers to run. Comment out if
# you want to avoid updating data for it.
# Most distros will usually come with both python & python3 installed.
python3 buildings.py
python3 courses.py
python3 evals.py
python3 exams.py
python3 food.py
python3 parking.py
python3 services.py
python3 textbooks.py
