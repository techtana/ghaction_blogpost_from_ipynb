FROM python:3.8-slim

LABEL version="1.0.0"
LABEL repository="https://github.com/techtana/ghaction_blogpost_from_ipynb"
LABEL homepage="https://github.com/techtana/ghaction_blogpost_from_ipynb"
LABEL maintainer="Tana T."

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY entrypoint.py /app/entrypoint.py

WORKDIR /app

ENTRYPOINT ["python", "/app/entrypoint.py"]
