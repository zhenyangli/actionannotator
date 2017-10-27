from glob import glob, iglob
import os


with open('A2D_videos.txt', 'r') as fp:
    videos = fp.read().splitlines()

vids = []
for video in videos:
    vid = video.split('/')[-1]
    vids.append(vid)


ants = []
annotations = sorted(glob('static/A2DEntities/*.xml'))
for annotation in annotations:
    ant = annotation.split('/')[-1].split('.')[0]
    ants.append(ant)


fp = open('A2D_ants.txt','w')
for v, vid in enumerate(vids):
    if not vid in ants:
        fp.write(str(v)+'\t'+vid+'\n')
fp.close()
