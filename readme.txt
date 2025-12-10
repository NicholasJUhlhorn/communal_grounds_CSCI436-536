Nicholas J Uhlhorn
November 2025

# Communal Grounds Server Readme

## Requirements
To run this application (spool up a server) one needs to have the following installed:
* docker

## Building (With makefile)
Use the makefile to run/build the project if you have docker-compose:
`make'

## Alternative Build/Run
To build the docker image manually run the following command: `docker build -t flask-app-docker .`

### Running
To run the server run the following command: `docker run -p 5001:5001 flask-app-docker`\\
The application will be ran locally on port 5001.
