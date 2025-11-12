from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import yt_dlp
import os
import tempfile
import traceback

# Initialize Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/download', methods=['POST'])
def download_video():
    data = request.get_json()
    video_url = data.get("url")
    download_format = data.get("format", "video")
    quality = data.get("quality", "best")

    if not video_url:
        return jsonify({"error": "Missing YouTube URL"}), 400

    try:
        # Create a temporary directory for downloads
        temp_dir = tempfile.mkdtemp()
        output_template = os.path.join(temp_dir, '%(title)s.%(ext)s')

        # yt-dlp options
        ydl_opts = {
            'outtmpl': output_template,
            'format': 'bestvideo+bestaudio/best' if download_format == 'video' else 'bestaudio/best',
            'merge_output_format': 'mp4' if download_format == 'video' else 'mp3',
            'quiet': True,
            'noplaylist': True
        }

        # Download video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)
            final_file = filename.rsplit('.', 1)[0] + ('.mp4' if download_format == 'video' else '.mp3')

        # Return the downloaded file
        return send_file(final_file, as_attachment=True)

    except Exception as e:
        print("❌ Error:", traceback.format_exc())
        return jsonify({"error": str(e)}), 500


@app.route('/api/playlist', methods=['POST'])
def download_playlist():
    data = request.get_json()
    playlist_url = data.get("url")

    if not playlist_url:
        return jsonify({"error": "Missing Playlist URL"}), 400

    try:
        temp_dir = tempfile.mkdtemp()
        output_template = os.path.join(temp_dir, '%(title)s.%(ext)s')

        ydl_opts = {
            'outtmpl': output_template,
            'format': 'bestvideo+bestaudio/best',
            'yesplaylist': True,
            'quiet': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([playlist_url])

        files = os.listdir(temp_dir)
        return jsonify({
            "message": "Playlist downloaded successfully!",
            "files": files
        })

    except Exception as e:
        print("❌ Error:", traceback.format_exc())
        return jsonify({"error": str(e)}), 500


# ✅ Dynamic port for Render (important!)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
