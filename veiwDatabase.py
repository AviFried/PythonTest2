
from app.models import User, Video
from app import create_app
app = create_app()
with app.app_context():
    users = User.query.all()

    for user in users:
        print(user.email, user.password)

    videos = Video.query.all()

    for video in videos:
        print(video)

