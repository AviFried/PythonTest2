# main.py

import os
from datetime import datetime

import cv2
from flask import Blueprint, render_template, send_file, request, Response, redirect, url_for, flash
from flask_login import login_required, current_user

from . import db
from .models import Video, Comment
from werkzeug.utils import secure_filename
main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        # Get the uploaded file from the form
        uploaded_file = request.files['file']

        if uploaded_file:
            # Save the file to a designated folder
            video_filename = secure_filename(uploaded_file.filename)
            video_dir = "./video"
            thumbnail_dir = "./thumbnails"
            thumbnail_filename = f"thumbnail_{video_filename}.jpg"
            thumbnail_path = os.path.join(thumbnail_dir, thumbnail_filename)
            video_path = os.path.join(video_dir, video_filename)
            uploaded_file.save(os.path.normpath(f"C:/Users/avif3/PycharmProjects/PythonTest2/app/{video_path}"))
            # Generate and save a thumbnail
            generate_thumbnail(video_path, thumbnail_path)
            # Create a new Video instance and add it to the database
            new_video = Video(
                title=request.form['title'],
                description=request.form['description'],
                directory=video_path,
                thumbnail=thumbnail_path,  # You might want to generate a thumbnail
                user=current_user
            )

            db.session.add(new_video)
            db.session.commit()

            return redirect(url_for('main.videos'))

    return render_template('upload.html')


def generate_thumbnail(video_path, thumbnail_path):

    print(video_path, thumbnail_path)
    # Using opencv to read the first frame of the video
    cap = cv2.VideoCapture(os.path.normpath(f"C:/Users/avif3/PycharmProjects/PythonTest2/app/{video_path}"))
    ret, frame = cap.read()
    cap.release()

    # Resize the frame (adjust dimensions as needed)
    resized_frame = cv2.resize(frame, (640, 360))

    # Save the resized frame as a thumbnail
    print(os.path.normpath(f"C:/Users/avif3/PycharmProjects/PythonTest2/app/{thumbnail_path}"))
    cv2.imwrite(os.path.normpath(f"C:/Users/avif3/PycharmProjects/PythonTest2/app/{thumbnail_path}"), resized_frame)

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user = current_user)

@main.route('/delete_video/<video_id>')
@login_required
def delete_video(video_id):
    # Query the video by ID
    video = Video.query.get_or_404(video_id)

    # Check if the current user owns the video
    if video.user != current_user:
        flash('You are not authorized to delete this video.', 'danger')
        return redirect(url_for('main.profile'))

    for comment in Comment.query.all():
        if comment.video_id == video.id:
            try:
                db.session.delete(comment)
            except Exception as e:
                db.session.rollback()
                print(f'Error deleting comment: {str(e)}', 'danger')
    try:
        # Delete the video from the database
        video_path = video.directory
        db.session.delete(video)
        db.session.commit()
        os.remove(os.path.normpath(f"C:/Users/avif3/PycharmProjects/PythonTest2/app/{video_path}"))
        print('Video deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        print(f'Error deleting video: {str(e)}', 'danger')

        return redirect(url_for('main.profile'))

    return redirect(url_for('main.profile'))

@main.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    sort_by = request.args.get('sort_by', 'date')  # Default to sorting by date if not provided

    if query:
        # Perform the search using SQLAlchemy's like operator
        base_query = Video.query.filter(Video.title.ilike(f'%{query}%') | Video.description.ilike(f'%{query}%'))

        # Adjust the query based on the sorting parameter
        if sort_by == 'name':
            results = base_query.order_by(Video.title).all()
        elif sort_by == 'date':
            results = base_query.order_by(Video.release_date.desc()).all()
        else:
            results = []
    else:
        results = []

    return render_template('search.html', query=query, sort_by=sort_by, results=results)


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
    sort_by = request.args.get('sort_by', 'name')

    # Adjust your query based on the sorting criteria
    if sort_by == 'name':
        videos = Video.query.order_by(Video.title).all()
    elif sort_by == 'date':
        videos = Video.query.order_by(Video.release_date.desc()).all()
    else:
        videos = Video.query.all()

    return render_template('videos.html', videos=videos)


@main.route('/video_stream/<videoID>')
@login_required
def video_stream(videoID):
    video= db.session.get(Video, videoID)  # Replace with the actual path to your video file
    video_path = f"/{video.directory}"
    video_path = os.path.normpath(f"C:/Users/avif3/PycharmProjects/PythonTest2/app{video_path}")
    print(video_path)
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
