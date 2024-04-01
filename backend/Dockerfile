# Use an official Python runtime as a parent image
FROM python:3.9

# Set the working directory in the container to /code
WORKDIR /code

# Copy the requirements file into the container at /code
COPY requirements.txt /code/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the current directory contents into the container at /code/app
COPY . /code

# Run the app when the container launches
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]