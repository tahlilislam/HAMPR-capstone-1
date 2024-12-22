#!/bin/sh -ex

python3 -m http.server 5000 &
celery -A website.make_celery --beat --loglevel=info
