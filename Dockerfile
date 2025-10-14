# Python Image
FROM python:3.12

# Set Work Directory
WORKDIR /criwin

# Copy the rest of the code
COPY . .

# Install OS libraries
RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg

# Install packages
RUN pip install yt-dlp discord.py[voice] dotenv

# Command to run application
CMD ["python", "./main.py"] 