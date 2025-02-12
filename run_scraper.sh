#!/bin/bash

cd /Users/aureliengattipierrini/Desktop/summer-internship-scraper

poetry env use python3
eval "$(poetry env info --path)/bin/activate"

poetry run scrape