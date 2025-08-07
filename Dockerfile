FROM python:3.10-slim

# Instala ffmpeg para que yt-dlp pueda convertir a mp3
RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /app
COPY . .

# Instala dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto 5000 (Render lo usa automáticamente si definiste PORT=5000)
EXPOSE 5000

# Comando para iniciar el servidor (sin modo debug)
CMD ["python", "app.py"]
