This project contains the code for implementing a REST API for image recognintion.

The db folder contains the Dockerfile for using the MongoDB image from docker hub.

docker-compose.yml used for running the requirements and dockerize my app using docker-compose build and docker-compose up to create image of the specified requirements.

The web folder contains the main project file that is app.py and the inception model which is in the classify_image.py published by tensorflow github. I use that code and make necessary changes according to the need of my api.


The web folder also contains the requirements.txt where I write all the requirements needed while the corresponding Dockerfile is used to for interacting with docker hub to create image of the required technologies and essentially dockerize the app.

Contributor : Ankush Vasishta