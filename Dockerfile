# Python Image
FROM python:3.12

# Install OS libraries
RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg

# Install packages
RUN pip install yt-dlp discord.py[voice] dotenv

# Copy the rest of the code
COPY . .

# Command to run application
CMD ["python", "./main.py"] 