ARG PYTHON_VERSION=3.8
FROM python:${PYTHON_VERSION}
WORKDIR /usr/app/my-app
COPY . .
RUN chmod 555 ./entrypoint.sh
RUN pip install -r requirements.txt
ENTRYPOINT ./entrypoint.sh

