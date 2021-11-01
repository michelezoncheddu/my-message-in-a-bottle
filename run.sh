#!/usr/bin/env bash

export FLASK_APP=monolith
export FLASK_ENV=development
export FLASK_DEBUG=true
python -m spacy download en
flask run