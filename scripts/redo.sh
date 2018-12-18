#!/bin/sh

cat $1 | while read line
do
        filename=$(echo $line | cut -d',' -f2)
        length=$(wc -m < full_text_consts/$filename)

        echo "${line},${length}"
done
