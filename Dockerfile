FROM python:3.7-alpine

LABEL com.centurylinklabs.watchtower.enable="true"

WORKDIR /app
ADD . /app

RUN pip install --upgrade pip pipenv
RUN pipenv install --system

CMD ["python3", "-m", "index"]
