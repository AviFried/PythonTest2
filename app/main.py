# main.py

import os
from datetime import datetime

from flask import Blueprint, render_template, send_file, request, Response, redirect, url_for, flash
from flask_login import login_required, current_user

from . import db
from .models import Video, Comment

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user = current_user)


@main.route('/thumbnail/<thumbnail_dir>')
@login_required
def thumbnail(thumbnail_dir):
    return send_file(thumbnail_dir)


@main.route('/add_comment/<videoID>', methods=['POST'])
@login_required
def add_comment(videoID):
    video = Video.query.get_or_404(videoID)

    # Get the comment text from the form
    comment_text = request.form.get('comment')

    # Create a new comment
    new_comment = Comment(text=comment_text, timestamp=datetime.utcnow(), user=current_user, video=video)

    # Add the comment to the database
    db.session.add(new_comment)
    db.session.commit()

    flash('Comment added successfully!', 'success')

    return redirect(url_for('main.video', videoID=videoID))


@main.route('/video/<videoID>')
@login_required
def video(videoID):
    video = db.session.get(Video, videoID)
    return render_template('video.html', videoID=videoID, video = video)


@main.route('/videos')
@login_required
def videos():
    videos = Video.query.all()
    print(videos)
    return render_template('videos.html', videos=videos)


@main.route('/video_stream/<videoID>')
@login_required
def video_stream(videoID):
    video= db.session.get(Video, videoID)  # Replace with the actual path to your video file
    video_path = f"/{video.directory}"
    video_path = os.path.normpath(f"C:/Users/avif3/PycharmProjects/PythonTest2/app{video_path}")
    response = build_full_response(video_path)
    response.headers.add('Cache-Control', 'public, max-age=3600')  # Cache for 1 hour
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
    return send_file(video_path, mimetype='video/mp4')
