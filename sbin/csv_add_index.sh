#!/bin/bash

###############################################################################
# csv_add_index.sh
# ----------------
# Add an index column to an existing CSV
###############################################################################

if [ "$#" -ne 1 ] 
then
        echo -e "USAGE:\n\t./$(basename $0) <csv_path>\n"
        exit
fi

nl -w1 -s',' $1
