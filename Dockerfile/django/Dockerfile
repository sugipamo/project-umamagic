# ベースステージ
FROM python:3.10 AS base

# Update pip and install requirements
COPY requirements.txt /tmp/
RUN pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt

# 最終ステージ
FROM python:3.10 AS final

# Set environment variables (if needed again)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8

# Define arguments
ARG USERNAME=user
ARG GROUPNAME=umamagic
ARG UID=1000
ARG GID=1000

# Create user and group, and add user to docker group
RUN groupadd -g $GID $GROUPNAME && \
    useradd -m -s /bin/bash -u $UID -g $GID $USERNAME
# RUN groupadd -g 999 docker && \
# usermod -aG docker $USERNAME

# Set working directory
USER $USERNAME
WORKDIR /home/$USERNAME/sources
