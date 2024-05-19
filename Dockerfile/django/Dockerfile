FROM python:3.10

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONIOENCODING utf-8

# Define arguments
ARG USERNAME=user
ARG GROUPNAME=umamagic
ARG UID=1000
ARG GID=1000

# Update pip
RUN pip install --upgrade pip

# Install requirements
COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

# Create user and group
RUN groupadd -g $GID $GROUPNAME && \
    useradd -m -s /bin/bash -u $UID -g $GID $USERNAME

# Add user to the docker group
RUN groupadd -g 999 docker && \
    usermod -aG docker $USERNAME

# Set working directory
USER $USERNAME
WORKDIR /home/$USERNAME

# Create directory for sources
RUN mkdir sources
WORKDIR /home/$USERNAME/sources
