FROM python:3.9.18-alpine3.19


# Install the application dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./ ./
EXPOSE 5000

ENV CELERY_BROKER_URL=redis://red-ctcejc2j1k6c73ff116g:6379

RUN echo $CELERY_BROKER_URL

ENTRYPOINT [ "/bin/sh" ]
CMD [ "./celery.sh" ]    