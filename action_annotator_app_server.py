from flask import g, Flask, session, url_for, request, render_template, redirect
from glob import glob, iglob
import json
import math, random
import os
import xml.etree.ElementTree as ET
app = Flask(__name__)
app.secret_key = 'actionannotator'


from xml.dom import minidom

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="\t")

def comments_parser(comments):
    video = ET.parse( comments ).getroot()
    return prettify( video )


#setup dataset:
def make_video_dict():
    d = dict()
    videos = sorted(glob('static/A2D_annotation/for_annotation_new/*'))
    random.seed(1000)
    random.shuffle(videos)
    for i, video in enumerate(videos):
        video_number = str(i)
        video_name = video.split('/')[-1]
        video_file = ''.join(['/static/A2D_annotation/videos/', video_name[:-2], '.mp4'])
        video_ins = video_name[-1]
        # pre-load all frames
        video_frames = sorted(glob(''.join(['static/A2D_annotation/for_annotation_new/', video_name, '/*.png'])))
        video_frames = ['/'+frame for frame in video_frames]
        text_file = ''.join(['static/A2DEntities/', video_name,'.xml'])
        d[video_number] = (video_name, video_file, video_ins, video_frames, text_file)
    return d

video_dict = make_video_dict()
all_video_numbers = sorted(video_dict.keys(), key = lambda x:int(x))
total = len(all_video_numbers)
maxnum = total - 1


# Pages
@app.route('/')
def main_page():
    return render_template('demo.html')

@app.route('/register_annotator', methods=['POST'])
def register_annotator():
    if request.form['submit'] == 'Start':
        return render_template('signin.html')
    elif request.form['submit'] == 'View':
        video_number = all_video_numbers[0]
        return redirect('/view/video/'+str(video_number))
    else:
        pass

@app.route('/start_annotate', methods=['POST'])
def start_annotate():
    #global annotator
    #annotator = request.form['annotator']

    if request.method == 'POST':
        session['username'] = request.form['annotator']

    video_number = all_video_numbers[0]
    return render_template('example.html')

@app.route('/start_example', methods=['POST'])
def start_example():
    video_number = all_video_numbers[0]
    return redirect('/video/'+str(video_number))

@app.route('/submit_annotation/video/<video_number>', methods=['POST'])
def submit_annotation(video_number):
    caption = request.form['caption']
    #
    #pd_color = request.form['pd-color']
    #pd_object = request.form['pd-object']
    #pd_action = request.form['pd-action']
    #pd_position = request.form['pd-position']
    #pd_caption = pd_object + ' ' + pd_action
    #if pd_color:
    #    pd_caption = pd_color + ' ' + pd_caption 
    #if pd_position:
    #    pd_caption = pd_caption + ' ' + pd_position 
    
    #st_caption = request.form['st-caption']

    save_comment(caption, video_number)
    current = all_video_numbers.index(video_number)
    if current < maxnum:
        following = current+1
    else:
        following = 0
    return redirect('/video/'+str(following))

@app.route('/view/video/<video_number>',methods=['GET','POST'])
def annotation_page(video_number):
    if request.method == "POST":
        if video_number == 'GO':
            video_number = int(request.form['gopage'])
            if video_number > maxnum+1:
                video_number = maxnum+1
            elif video_number < 1:
                video_number = 1
            video_number = str(video_number - 1)
        else:
            pass
    elif request.method == 'GET':
        if video_number == 'RANDOM':
            video_number = random.choice(all_video_numbers)
        elif video_number == 'FIRST':
            video_number = all_video_numbers[0]
        elif video_number == 'LAST':
            video_number = all_video_numbers[-1]
    current = all_video_numbers.index(video_number)
    if current > 0:
        previous = url_for_view_image(all_video_numbers[current-1])
    else:
        previous = None
    if current < maxnum:
        following = url_for_view_image(all_video_numbers[current+1])
    else:
        following = None
    if video_number in video_dict:
        video_name, video, video_ins, video_frames, comments = video_dict[video_number]
        if os.path.isfile(comments):
            comments_data = comments_parser(comments)
        else:
            comments_data = ''
        
        #num_frames = len(video_frames)
        
        #
        return render_template('annotation_page.html',
                                video_name = video_name,
                                video_number = video_number,
                                video = video,
                                frames = video_frames,
                                current = current,
                                total = total,
                                comments = comments_data,
                                previous = previous,
                                following = following)


@app.route('/video/<video_number>',methods=['GET','POST'])
def annotator_page(video_number):
    if request.method == "POST":
        if video_number == 'GO':
            video_number = int(request.form['gopage'])
            if video_number > maxnum+1:
                video_number = maxnum+1
            elif video_number < 1:
                video_number = 1
            video_number = str(video_number - 1)
        else:
            pass
    elif request.method == 'GET':
        if video_number == 'RANDOM':
            video_number = random.choice(all_video_numbers)
        elif video_number == 'FIRST':
            video_number = all_video_numbers[0]
        elif video_number == 'LAST':
            video_number = all_video_numbers[-1]
    current = all_video_numbers.index(video_number)
    if current > 0:
        previous = url_for_image(all_video_numbers[current-1])
    else:
        previous = None
    if current < maxnum:
        following = url_for_image(all_video_numbers[current+1])
    else:
        following = None
    if video_number in video_dict:
        video_name, video, video_ins, video_frames, comments = video_dict[video_number]
        if os.path.isfile(comments):
            comments_data = comments_parser(comments)
        else:
            comments_data = ''

        #num_frames = len(video_frames)

        #
        return render_template('annotator_page.html',
                                video_name = video_name,
                                video_number = video_number,
                                video = video,
                                frames = video_frames,
                                current = current,
                                total = total,
                                comments = comments_data,
                                previous = previous,
                                following = following)


# Logic
def url_for_image(video_number):
    return url_for('annotator_page', video_number=video_number)

def url_for_view_image(video_number):
    return url_for('annotation_page', video_number=video_number)

def save_comment(caption, video_number):
    current = all_video_numbers.index(video_number)
    if video_number in video_dict:
        video_name, video, video_ins, video_frames, comments = video_dict[video_number]
        #annotation = {'video': video_name,'caption': comment,'consistency': consistency,'annotator': 'Anonymous'}
        #with open(comments, 'a') as f:
            #f.write('\n------------------\Video: ' + str(video_number) + '\n')
            #f.write(annotator + '; ' + invarfeat + '; ' + varfeat + '; ' + caption + '\n')
        if 'username' in session:
            annotator = session['username']
        if os.path.exists(comments):
            video = ET.parse( comments ).getroot()
            annotation = ET.SubElement(video, 'annotation')
            node_user = ET.SubElement(annotation, 'user')
            node_user.text = annotator
            node_caption = ET.SubElement(annotation, 'caption')
            node_caption.text = caption
            #node_pd_caption = ET.SubElement(annotation, 'pd_caption')
            #node_pd_caption.text = pd_caption
            #node_st_caption = ET.SubElement(annotation, 'st_caption')
            #node_st_caption.text = st_caption

            output_file = open( comments, 'w' )
            output_file.write( ET.tostring( video ) )
            output_file.close()

        else:
            video = ET.Element('video')
            filename = ET.SubElement(video, 'filename')
            filename.text = video_name
            annotation = ET.SubElement(video, 'annotation')
            node_user = ET.SubElement(annotation, 'user')
            node_user.text = annotator
            node_caption = ET.SubElement(annotation, 'caption')
            node_caption.text = caption
            #node_pd_caption = ET.SubElement(annotation, 'pd_caption')
            #node_pd_caption.text = pd_caption
            #node_st_caption = ET.SubElement(annotation, 'st_caption')
            #node_st_caption.text = st_caption

            output_file = open( comments, 'w' )
            output_file.write( ET.tostring( video ) )
            output_file.close()
        


if __name__ == '__main__':
    app.debug = True
    app.run(host='146.50.28.35')
    #app.run(host='127.0.0.1')
