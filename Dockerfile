# Python Image
FROM python:3.12-slim

# Set Work Directory
WORKDIR /criwin

# Install OS libraries
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y ffmpeg libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

    # Create required directories
RUN mkdir -p cache/sounds downloads

RUN pip install --no-cache-dir \
    yt-dlp \
    discord.py[voice] \
    dotenv \
    psycopg2-binary \
    minio \
    gallery-dl \
    pillow

# Copy cookies file
COPY www.youtube.com_cookies.txt ./www.youtube.com_cookies.txt
COPY www.instagram.com_cookies.txt ./www.instagram.com_cookies.txt

# Copy application code
COPY src/ ./src/
COPY main.py .

# Command to run application
CMD ["python", "main.py"]