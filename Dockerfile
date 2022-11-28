FROM python:3.10.5-bullseye as base

USER root
RUN apt-get update && apt-get install sqlite3

RUN useradd -m ttt
RUN mkdir /app
RUN chown ttt:ttt /app

FROM base AS pythonbase

USER ttt

WORKDIR /app
COPY requirements.txt .

RUN pip install -r requirements.txt

FROM pythonbase AS app

RUN mkdir db
COPY static static
COPY templates templates
COPY app.py .

ENV FLASK_APP=app

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]