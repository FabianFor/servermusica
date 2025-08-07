from flask import Flask, request, jsonify, send_from_directory
import yt_dlp
import os
import re

app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*\n\r]', '_', filename)

@app.route('/download', methods=['POST'])
def download_audio():
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    if not os.path.exists('cookies.txt'):
        return jsonify({"error": "Archivo cookies.txt no encontrado en el servidor"}), 500

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
        'quiet': True,
        'cookiefile': 'cookies.txt',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            downloaded_path = ydl.prepare_filename(info)
            base, _ = os.path.splitext(downloaded_path)
            final_path = base + ".mp3"
            filename = sanitize_filename(os.path.basename(final_path))

        return jsonify({"message": "Download completed", "file": filename})

    except yt_dlp.utils.DownloadError:
        return jsonify({"error": "No se pudo descargar el video. Puede que esté restringido o no disponible sin login."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/downloads/<path:filename>', methods=['GET'])
def get_file(filename):
    file_path = os.path.join(DOWNLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

# ⚠️ Este bloque solo se ejecuta localmente, así que lo eliminamos
# if __name__ == '__main__':
#     port = int(os.environ.get('PORT', 5000))
#     app.run(host='0.0.0.0', port=port, debug=True)
