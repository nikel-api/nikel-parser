# Nikel Parser

Dataset parser for Nikel API

Since websites can often change layouts, and things can break. This repo contains a hodgepodge of Python scripts that aren't intended to be robust.

### Setup

Make sure you've installed the Selenium Chrome Driver:

* via [Official Site](https://sites.google.com/a/chromium.org/chromedriver/)
* via Chocolatey: `choco install selenium-chrome-driver`

To install all python packages required for scraping and parsing: `pip install requirements.txt`

### Folders

* `data`: contains datasets for Nikel API.
* `data_parser`: contains scraper code for generating datasets. To update a dataset, run the respective python file.
* `pickles`: stores various temporary python objects and data.
* `snapshots`: stores backups of JSON payloads for emergency backup purposes.
* `config`: currently useless.
