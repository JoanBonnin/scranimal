#!/bin/bash

file=dataset.csv

if [ -f $file ] ; then
    rm $file
fi

echo "Logging crawler activity at \"scrapy.log\""

scrapy crawl adopting -o $file -t csv
