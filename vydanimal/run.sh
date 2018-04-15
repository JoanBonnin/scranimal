#!/bin/bash

file=dataset.csv

if [ -f $file ] ; then
    rm $file
fi

scrapy crawl adopting -o $file -t csv
