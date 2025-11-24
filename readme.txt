Nicholas J Uhlhorn
November 2025

# Communal Grounds Server Readme

## Requirements
To run this application (spool up a server) one needs to have the following installed:
* docker

## Building
To build the docker image manually run the following command: `docker build -t flask-app-docker .`

## Running
To run the server run the following command: `docker run -p 5000:5000 flask-app-docker`\\
The application will be ran locally on port 5000.

## Alternative Build/Run
You may also use the makefile to run/build the project if you have docker-compose.
