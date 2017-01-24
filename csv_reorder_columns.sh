#!/bin/bash

###############################################################################
# This script will re-order the columns in a CSV
#
# ./csv_reorder_columns.sh 2,1 "<col1>,<col2>" => "<col2>,<col1>"
###############################################################################

if [ "$#" -ne 2 ] 
then
        echo -e "USAGE:\n\t./$(basename $0) 1,3,2 myfile.csv"
        exit
fi


# Set internal field separator to be a comma
IFS=','; 

# Make an array out of the first argument (e.g. "2,1,3")
COLUMNS=($1); 

# Return the IFS to its default of " "
unset IFS;

AWK_REORDER="";

for col in ${COLUMNS[@]}
do
        AWK_REORDER="${AWK_REORDER}\$${col} \",\" ";
done

AWK_REORDER="{ print ${AWK_REORDER} }";


# Awk with ',' delimiter and escaped ',' inside of double quotes
awk -vFPAT='([^,]*)|("[^"]+")' -vOFS=, "$AWK_REORDER" $2


#awk -vFPAT='([^,]*)|("[^"]+")' -vOFS=, '{ print $1 "," $3 "," $2 "," $4 "," $5 "," $6 "," $7}' newmeta.csv 
# Awk with ',' delimiter and escaped ',' inside of double quotes
#awk -vFPAT='([^,]*)|("[^"]+")' -vOFS=, '{ print $1 "," $3 "," $2 "," $4 "," $5 "," $6 "," $7}' newmeta.csv 
