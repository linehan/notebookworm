#!/bin/sh
###############################################################################
# Create a bookworm JSON catalog 
###############################################################################

for filename in $(\ls --ignore=$(basename $0) .)
do
        # Example filename: "Dominican_Republic_1821.txt"

        # Captures all but the last section delimited by '_' 
        country=$(echo $filename | sed -r 's/(_[^_]+){1}$//g')

        # Captures the last section delmited by '_'
        year=$(echo $filename | rev | cut -d'.' -f2 | cut -d'_' -f1 | rev)

        echo "$filename,$year,$country"
done
