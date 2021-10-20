#!/bin/bash

source ./project.settings

#Start chat and feed app
uvicorn app.main:app --host 0.0.0.0 --port $PORT \
  --reload \
  --reload-dir ./app \
  --reload-dir ./configs \
  --reload-dir ./models \
  --reload-dir ./tests
