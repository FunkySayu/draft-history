# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the content of the local src directory to the working directory
# This will copy app.py and any other Python files.
COPY . .

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable for Flask
ENV FLASK_APP app.py
ENV FLASK_RUN_HOST 0.0.0.0
# DATABASE_URL will be set via docker-compose

# Install gunicorn for a more production-ready server
RUN pip install gunicorn

# Run app.py when the container launches using Gunicorn
# Gunicorn will pick up FLASK_APP.
# The app.py has been modified to accept DATABASE_URL from env var.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
