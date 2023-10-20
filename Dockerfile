# Use an official Python runtime as a parent image
FROM python:3.10

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install build dependencies
RUN apt-get update && apt-get install -y gcc

# Set work directory
WORKDIR /code

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /code/
COPY . .

# Make port 8000 available to the world outside this container
EXPOSE 8000

