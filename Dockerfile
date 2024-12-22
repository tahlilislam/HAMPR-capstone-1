FROM python:3.9.18-alpine3.19


# Install the application dependencies
COPY requirements.txt ./
RUN \
 apk add --no-cache python3 postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc python3-dev musl-dev postgresql-dev && \
 python3 -m pip install -r requirements.txt --no-cache-dir && \
 apk --purge del .build-deps

COPY ./ ./
EXPOSE 5000

ENV CELERY_BROKER_URL=redis://red-ctcejc2j1k6c73ff116g:6379

RUN echo $CELERY_BROKER_URL

ENTRYPOINT [ "/bin/sh" ]
CMD [ "./celery.sh" ]    