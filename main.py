# main.py

from flask import Blueprint, render_template, send_file, request, Response
from flask_login import login_required, current_user
import os
from client import client
client = client()
db = client.totalData
video_collection = db.videos
main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)

@main.route('/thumbnail/<thumbnail_dir>')
@login_required
def thumbnail(thumbnail_dir):
    return send_file(thumbnail_dir)

@main.route('/video/<videoID>')
@login_required
def video(videoID):
    return render_template('video.html', videoID=videoID)

@main.route('/videos')
@login_required
def videos():
    videos = video_collection

    return render_template('videos.html', videos= videos)

@main.route('/video_stream/<videoID>')
@login_required
def video_stream(videoID):
    video_path = videoID  # Replace with the actual path to your video file

    range_header = request.headers.get('Range', None)
    video_size = os.path.getsize(video_path)

    if range_header:
        byte_ranges = parse_range_header(range_header, video_size)
        response = build_partial_response(byte_ranges, video_path)
    else:
        response = build_full_response(video_path)

    return response

def parse_range_header(range_header, video_size):
    ranges = range_header.replace('bytes=', '').split('-')
    start = int(ranges[0]) if ranges[0] else 0
    end = int(ranges[1]) if ranges[1] else video_size - 1
    return (start, end)

def build_partial_response(byte_ranges, video_path):
    start, end = byte_ranges
    length = end - start + 1

    with open(video_path, 'rb') as video_file:
        video_file.seek(start)
        data = video_file.read(length)

    response = Response(data, 206, mimetype='video/mp4', content_type='video/mp4', direct_passthrough=True)
    response.headers.add('Content-Range', f'bytes {start}-{end}/{length}')
    return response

def build_full_response(video_path):
    return send_file(video_path, mimetype='video/mp4', cache_timeout=-1)