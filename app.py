import json
import os
import requests
from flask import Flask, request
from textwrap import wrap
import matplotlib.pyplot as plt
from flask import render_template
from operator import itemgetter
from datetime import datetime
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, \
    VideoUnavailable, TooManyRequests, TranscriptsDisabled, \
    NoTranscriptAvailable
from transformers import pipeline
from pytube import YouTube

# Create an instance of Flask object.
app = Flask(__name__, template_folder='templates', static_folder='static')

# Add this line to enable hot reloading
app.config['TEMPLATES_AUTO_RELOAD'] = True

# ... (rest of your code)
# Youtube developer API
api_key = 'AIzaSyCUKN1xNCoHv9W-QYb0e-zrRiRS0CKRoSw'
pwd = os.getcwd()

# Function will take care of transcript related exceptions.
def get_transcript(video_id):
    try: 
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        res = ""
        for i in transcript:
            res += " " + i['text']
        return res
    except VideoUnavailable: 
        error = "Video not available"
        return render_template('summary.html', summary=error)
    except TranscriptsDisabled:
        error = "Transcripts disabled for this video."
        return render_template('summary.html', summary=error)
    except NoTranscriptAvailable:
        error = 'Tanscripts are not available for this video.'
        return render_template('summary.html', summary=error)
    except NoTranscriptFound:
        error = "Transcripts not found for this video."
        return render_template('summary.html', summary=error)
    except:
        error = "Could not find transcript for this video link."
        return render_template('summary.html', summary=error)


# Get Channel Statistics for Data analysis.


# Summarize transcript using hugging face transformer.
def summary(transcript):
    
    # Pipeline for summarize transcript.
    summarizer = pipeline('summarization')

    # Transformer accpets 1024 words for summarization, 
    # Hence spltiing the transcript according to requirement.
    num_iters = int(len(transcript)/1000)
    summarized_text = []
 
    if (num_iters == 0):
        return transcript
 
    # Summarize every split and append to create complete summaziration.
    for i in range(0, num_iters + 1):
        start = 0
        start = i * 1000
        end = (i + 1) * 1000
        
        out = summarizer(transcript[start:end])
        out = out[0]
        out = out['summary_text']
        
        summarized_text.append(out)

    # Return complete summarization.
    return summarized_text
    

final_result = []

# Defining resource endpoints, Flask call start() on invoking /api/summarize
@app.route('/api/summarize', methods = ['GET'])
def start():

    # Save youtube_url fetched from chrome extention
    youtube_url = request.args.get("youtube_url")
    yotube_url = youtube_url.split("=")
 
    # Fetch video_id from url.
    try:
        video_id = yotube_url[1]
        youtube_obj = YouTube(youtube_url)
    except IndexError:
        return render_template('summary.html', summary="URL not compatible.")

    # Fetch channel_id for channel stats. 
    channel_id = youtube_obj.channel_id

    # Call get_stats for channel and video stats required for data analysis. 
   
    

    # Fetch transcript using video_id.
    transcript = get_transcript(video_id)
    # print(transcript)
    result = summary(transcript)
    final_result = result

    # Render summary.html.
    return render_template('summary.html', summary=result)
# server the app when this file is run
if __name__ == '__main__':
    app.run()
