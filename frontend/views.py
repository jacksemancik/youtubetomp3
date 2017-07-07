from django.shortcuts import render_to_response, render
from django.http import HttpResponse
from frontend.models import VideoURL, Video, VideoURLForm
import subprocess
from downloader.views import get_video_info, create_filename
import re
from unicodedata import normalize
import os


def home(request):
    return render_to_response('home.html', {"form":VideoURLForm})

def slugger(text, delim='-'):

    result = []

    re_obj = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.:]+')
    for word in re_obj.split(text):
        word = normalize('NFKD', word).encode('ascii', 'ignore').decode('utf-8')
        word = word.replace('/', '')
        if word:
            result.append(word)

    return delim.join(result)
# Create your views here.

def convert(url):
    subprocess.call('./static/rmfolder.sh', cwd=os.path.dirname(os.path.realpath(__file__)))
    info = get_video_info(url)
    if info:
        duration = info.get('duration')
    if info and duration and duration <= settings.MAX_DURATION_SECONDS:
        youtube_id = info['id']
        title = info['title']
        audio_filename = create_filename(info['title'])
        video, created = Video.objects.get_or_create(youtube_id=youtube_id)
        video.url = url
        video.title = title
        video.duration = duration
        video.audio_filename = audio_filename
        video.timestamp = datetime.datetime.now()
        video.save()
    result = subprocess.check_call([
        'youtube-dl',
        '--no-playlist',
        '--extract-audio',
        '--audio-format', 'mp3',
        '--output', 'temp',
        '--cache-dir', '/tmp/youtube-dl',
        url,
    ])
    if result == 0:
        return render_to_response('download.html', {"filename":audio_filename})
    else:
        return render_to_response('500.html')
