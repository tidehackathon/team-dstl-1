#!/bin/bash

for i in {0..15}
do
    python3 extract.py -v "/home/james/data/videos/sample5/full_video.mp4" -o 1568122109 -l "/home/james/data/videos/sample5/2019-09-10 16-18-38.tlog" -x $((1568122126 + (10*i)))
    mv extracted.jpg extracted_$i.jpg
    mv extracted.json extracted_$i.json
done