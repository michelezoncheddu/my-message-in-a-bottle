# my-message-in-a-bottle
[![Build Status](https://app.travis-ci.com/michelezoncheddu/my-message-in-a-bottle.svg?token=25pb1vpf8utiQzbEtn9M&branch=main)](https://app.travis-ci.com/michelezoncheddu/my-message-in-a-bottle)
[![Coverage Status](https://coveralls.io/repos/github/michelezoncheddu/my-message-in-a-bottle/badge.svg?branch=main)](https://coveralls.io/github/michelezoncheddu/my-message-in-a-bottle?branch=main)

### Setup the environment

To setup the environment, you should follow these steps:

1. Open the project in your IDE.
2. From IDE terminal, or normal Ubuntu/MacOS terminal execute the command `virtualenv venv` inside project root.
3. Now, you have to activate it, by executing the command `source venv/bin/activate`.
4. You have to install all requirements, let's do that with `pip install -r requirements.txt`.

### Run the application

If you want to run the application WITH docker, yopu have to execute the following commands:

1. `docker-compose build`
2. `docker-compose app`

If you want to run the application WITHOUT docker, you have to execute the following commands:

1. Run the script `run.sh` by typing `bash run.sh`
2. Run redis `docker run -d -p 6379:6379 redis`
3. `celery --app monolith.background worker -l INFO`
4. `celery --app monolith.background beat -l INFO`
