from flask import Flask, request, jsonify, send_from_directory
import yt_dlp
import os

app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/download', methods=['POST'])
def download_audio():
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),  # guarda con extensión original
        'quiet': True,
        # Sin postprocesadores para evitar necesidad de ffmpeg
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
        filename = f"{info['title']}.{info['ext']}"  # extensión real que se descargó
        return jsonify({"message": "Download completed", "file": filename})
    except yt_dlp.utils.DownloadError:
        return jsonify({"error": "No se pudo descargar el video. Puede que esté restringido o no disponible sin login."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/downloads/<path:filename>', methods=['GET'])
def get_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    import sys
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
