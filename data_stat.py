import numpy as np
import os
import json

from glob import glob, iglob
import xml.etree.ElementTree as ET


################################################################################
# Load annotations
################################################################################
with open('A2D_videos.txt', 'r') as fp:
    videofiles = fp.read().splitlines()

videos = []
for videofile in videofiles:
    video = videofile.split('/')[-1]
    videos.append(video)


################################################################################
# Collect training samples
################################################################################
descriptions = []
for v, video in enumerate(videos):

    query_file = 'static/A2DEntities/' + video + '.xml'
    root = ET.parse(query_file).getroot()
    # querier = prettify( querier )

    qid = 1
    description = root[qid][1].text
    descriptions.append(description)

with open('All_Annotations.txt', 'w') as fp:
    for description in descriptions:
        fp.write(description+'\n')

        