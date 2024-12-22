#!/bin/sh -ex

python3 -m http.server 5000 &
celery -A tasks worker --beat --loglevel=info