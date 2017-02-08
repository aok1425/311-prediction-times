#!/bin/bash

for fullfile in *.png
do
	filename=$(basename "$fullfile")
	filename="${filename%.*}"
	cp $fullfile $filename-small.png
	sips -Z 300 $filename-small.png
done