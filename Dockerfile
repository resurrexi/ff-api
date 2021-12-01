# Pull base image
FROM python:3.8-slim

# Set env vars
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Update packages
RUN apt-get update && \
    apt-get -y upgrade

# Set working directory
WORKDIR /usr/src/app

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy project
COPY . .

# Create "files" directory
RUN mkdir /usr/src/app/files
