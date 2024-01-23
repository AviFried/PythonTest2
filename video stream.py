from flask import Flask, render_template, send_file, request, Response
import os
app = Flask(__name__)


@app.route('/video/<videoID>')
def video(videoID):
    return render_template('video.html', videoID=videoID)

@app.route('/video_stream/<videoID>')
def video_stream(videoID):
    video_path = video_files[videoID]  # Replace with the actual path to your video file

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
    return send_file(video_path, mimetype='video/mp4')

if __name__ == '__main__':
    app.run(debug=True)
