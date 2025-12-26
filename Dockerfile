# Python Image
FROM python:3.12

# Set Work Directory
WORKDIR /criwin

# Copy the rest of the code
COPY src/ ./src/
COPY main.py .
COPY cookies.txt .
COPY .env.prod .env

# Install OS libraries
RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg

# Create required directories
RUN mkdir -p cache/sounds downloads

# Install packages
RUN pip install yt-dlp discord.py[voice] dotenv boto3 cloudflare gallery-dl pillow

# Command to run application
CMD ["python", "main.py"] 