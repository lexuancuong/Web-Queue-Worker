# syntax=docker/dockerfile:1.0.0-experimental
FROM python:3.7

ENV PYTHONUNBUFFERED 1

WORKDIR /tmp/src/webapp

RUN pip install --upgrade pip

RUN apt-get -yq update
RUN apt-get -yqq install ssh
RUN apt-get install git
RUN mkdir -p -m 0600 ~/.ssh && ssh-keyscan github.com >> ~/.ssh/known_hosts

RUN --mount=type=ssh ssh -T git@github.com 2>&1 | grep 'successfully authenticated'

# RUN --mount=type=ssh pip install --default-timeout=10000 lib-layout[jeff]@git+ssh://git@github.com/Cinnamon/lib-layout.git@v0.11.0 --find-links https://download.pytorch.org/whl/torch_stable.html
# RUN --mount=type=ssh pip install --default-timeout=10000 lib-ocr[cannet]@git+ssh://git@github.com/Cinnamon/lib-ocr.git@v2.13.0

COPY . .

RUN pip install --no-cache-dir -r ./requirements.txt

CMD ["sh", "-c", "python main.py; celery -A webapp worker --c 2;"]