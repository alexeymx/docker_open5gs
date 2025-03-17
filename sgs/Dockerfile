# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
ENV TERM xterm
# Make port 29118 available to the world outside this container
EXPOSE 29118

# Run server.py when the container launches
CMD ["python", "server.py"]