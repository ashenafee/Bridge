# Use an official Node.js runtime as a parent image
FROM node:current-alpine

# Set the working directory in the container to /code
WORKDIR /code

# Copy the package.json file into the container at /code
COPY package.json /code/package.json

# Install any needed packages specified in package.json
RUN npm install

# Copy the current directory contents into the container at /code
COPY . /code

# Serve the app
CMD ["npm", "run", "dev"]