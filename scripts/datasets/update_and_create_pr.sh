#!/bin/bash
set -e
bash $PROJECT_DIR/nikel-parser/scripts/datasets/update_local_data.sh
bash $PROJECT_DIR/nikel-parser/scripts/datasets/create_new_data_pr.sh
