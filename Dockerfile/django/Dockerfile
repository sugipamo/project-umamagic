FROM python:3.10
ENV PATH $PATH:/home/user/.local/lib/python3.10/Scripts
# ENV PIPENV_VENV_IN_PROJECT=1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONIOENCODING utf-8
ENV TZ="Asia/Tokyo"
ENV LANG=C.UTF-8
ENV LANGUAGE=en_US:en_US
ENV SELENIUM_URL=http://selenium:4444/wd/hub

ARG USERNAME=user
ARG GROUPNAME=umamagic
ARG UID=1000
ARG GID=1000

RUN groupadd -g $GID $GROUPNAME && \
    useradd -m -s /bin/bash -u $UID -g $GID $USERNAME
USER $USERNAME
WORKDIR /home/$USERNAME
RUN mkdir sources
WORKDIR /home/$USERNAME/sources

RUN pip install --upgrade pip && \ 
    pip install pipenv

