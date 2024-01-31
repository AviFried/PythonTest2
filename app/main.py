# main.py

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
    return render_template('profile.html', user=current_user)


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

    return redirect(url_for('video.watch', videoID=videoID))
