# Nikel Parser

Dataset parser for Nikel API

Since websites can often change layouts and things can break, this repo contains a hodgepodge of Python scripts that aren't intended to be robust.

## Thanks

* Heavily inspired by [Cobalt API](https://github.com/cobalt-uoft/cobalt) and huge thanks to their amazing work.

## Setup

To install all python packages required for scraping and parsing: `pip install requirements.txt`

Some scripts require that you install the Selenium Chrome Driver:

* via [Official Site](https://sites.google.com/a/chromium.org/chromedriver/)
* via Chocolatey: `choco install selenium-chrome-driver`

Very rarely, some scripts will require university authentication. In this case, you must set the environment variables `UTOR_USERNAME` and `UTOR_PASSWORD` with valid credentials.

## Folders

* `data`: contains datasets for Nikel API.
* `data_parser`: contains scraper code for generating datasets. To update a dataset, run the respective python file.
* `pickles`: stores various temporary python objects and data.
* `snapshots`: stores backups of JSON payloads for emergency backup purposes.
* `config`: currently useless.
