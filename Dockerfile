FROM python:3.10
WORKDIR /app
COPY . /app
RUN pip3 --no-cache-dir install -r requirements.txt
CMD [ "gunicorn", "-b", "0.0.0.0:5000", "app:app"]