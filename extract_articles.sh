#!/usr/bin/env bash
# -------------------------------------------------------------------------------
# Name: 
# Purpose: 
# Version: 1.0
# Date: 
# Author: Mark Saum
# Email: mark@saum.net
# -------------------------------------------------------------------------------

VAULT_PATH="/mnt/c/Users/msaum.FIDELISCORP/iCloudDrive/iCloud~md~obsidian/MicroGrids"

for MDFILE in *.md
do
    echo "Processing: ${MDFILE}"
    python3 ${VAULT_PATH}/scripts/url2md.py "${MDFILE}" --output-dir ${VAULT_PATH}/articles
done
