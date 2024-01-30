import os
import cv2
from app.models import Video, User
from app import create_app, db


def updateVideos():
    video_dir = "video"
    thumbnail_dir = "thumbnails"

    for video_filename in os.listdir(video_dir):
        video_path = os.path.join(video_dir, video_filename)
        print(video_filename)

        thumbnail_filename = f"thumbnail_{video_filename}.jpg"
        thumbnail_path = os.path.join(thumbnail_dir, thumbnail_filename)

        # Check if the video already exists in the database
        existing_video = Video.query.filter_by(directory=video_path).first()

        if not existing_video:
            # Insert the video into the database
            new_video = Video(directory=video_path, thumbnail=thumbnail_path, title=video_filename.split(".")[0],
                              description="Testing Video", user_id=1)

            # Assuming there is a user with id=1 (replace it with an appropriate user id)
            user = User.query.get(1)
            new_video.user = user

            # Generate and save a thumbnail
            generate_thumbnail(video_path, thumbnail_path)

            # Add the new video to the database
            db.session.add(new_video)
            db.session.commit()
        else:
            # Assuming you want to update the thumbnail path if the video already exists
            existing_video.thumbnail = thumbnail_path
            db.session.commit()


def generate_thumbnail(video_path, thumbnail_path):
    # Using opencv to read the first frame of the video
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    cap.release()

    # Resize the frame (adjust dimensions as needed)
    resized_frame = cv2.resize(frame, (640, 360))

    # Save the resized frame as a thumbnail
    cv2.imwrite(thumbnail_path, resized_frame)


if __name__ == "__main__":
    app = create_app()
    # Use a context manager to ensure proper setup and teardown of the app context
    with app.app_context():
        # Delete all existing videos
        db.session.query(Video).delete()

        # Commit the deletion
        db.session.commit()

        # Run the function to update videos
        updateVideos()