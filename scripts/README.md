# Scripts
A collection of useful scripts for getting stuff done. The following is assumed about the current state of your local machine:
- The environment variable `PROJECT_DIR` with value of where nikel-parser is cloned into
    - e.g. `export PROJECT_DIR="~/projects/nikel-parser"`
- The package [hub](https://github.com/github/hub) is already installed for your system
    - This is used to create PRs via CLI
- All other configurations for the parser are in place
    - e.g. selenium drivers, UofT authentication (if required), etc.

The scripts are assumed to be run from the project root.

## Overview

### Dataset Scripts
#### `update_and_create_pr.sh`
Does both of the actions described below, in order.

#### `update_local_data.sh`
Runs all parsers. To exclude a parser, simply comment it out inside the file.

#### `create_new_data_pr.sh`
Creates a new branch & PR for the updated JSON data and pickels, where the names are suffixed by the current date and time.

## Setting up a cron job
To configure a cron job for periodically updating the dataset, do:
1. Make sure both scripts are executable `chmod +x scripts/create_new_data_pr.sh scripts/update_local_data.sh`
2. cron service should be active `systemctl status crontab`
3. Update existing jobs `crontab -e`
4. In a new line, enter: `0 3 * * * ./path/to/script`

That's it! The data will now update at 3AM every day.