from client import client
client = client()
import os
import cv2
from pymongo.collation import Collation



def updateVideos():
    db = client.totalData
    video_collection = db.videos
    video_dir = "video"
    thumbnail_dir = "thumbnails"

    for video_filename in os.listdir(video_dir):
        video_path = os.path.join(video_dir, video_filename)
        print(video_filename)

        thumbnail_filename = f"thumbnail_{video_filename}.jpg"
        thumbnail_path = os.path.join(thumbnail_dir, thumbnail_filename)

        # Check if the video already exists in the database
        existing = video_collection.find_one({"directory": video_path})

        if not existing:
            # Insert the video into the database
            video_collection.insert_one({"directory": video_path, "thumbnail": thumbnail_path})

            # Generate and save a thumbnail
        generate_thumbnail(video_path, thumbnail_path)


def generate_thumbnail(video_path, thumbnail_path):
    # Using opencv to read the first frame of the video
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    cap.release()

    # Resize the frame (adjust dimensions as needed)
    resized_frame = cv2.resize(frame, (640, 480))

    # Save the resized frame as a thumbnail
    cv2.imwrite(thumbnail_path, resized_frame)

def parseVideos():
    db = client.totalData
    video_collection = db.videos

    print(video_collection.find())
    for video in video_collection.find():
        print(video)
if __name__ == "__main__":
    updateVideos()
    #parseVideos()