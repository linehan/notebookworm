#!/bin/bash

###############################################################################
# csv_sort_reindex.sh
# -------------------
# Sort a CSV and re-index it after the sort 
###############################################################################

if [ "$#" -ne 2 ] 
then
        echo -e "USAGE:\n\t./$(basename $0) <col_to_sort> <csv_path>\n"
        echo -e "NOTE:\n\t Assumes rows are indexed by first column"
        exit
fi

# 
# Beautiful...
#
# Remove the first column, sort on the (new) first column, 
# and re-index after sort.
#
# cut -d',' -f2- $2 | sort -t',' -k1 | nl -w1 -s','


sort_on=$1
sort_on=$((sort_on - 1)) # because we are removing the first (index) column

cut -d',' -f2- $2 | sort -t',' -k$sort_on | nl -w1 -s','
