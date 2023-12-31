# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container to /app
WORKDIR /app

# Copy the requirements.txt file into the container at /app
COPY requirements.txt /app

# Install the required packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Add the rest of the application code
COPY app/ /app

# Make port 80 available to the world outside this container
EXPOSE 80

# Run app/main.py when the container launches
CMD ["python", "main.py", "--host", "0.0.0.0", "--port", "80"]

