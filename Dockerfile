# Build Docker image
#
# 1. From windows command line change directory to directory with this file
# 2. Run docker build: docker build -t  [Container registry of your choice]/sequoia:latest .   EXAMPLE: docker build -t wsdotdev.azurecr.io/sequoia:latest .
# 3. Run docker image: docker run -p 8000:8000 [image id]  Image id comand: docker image ls

# PUSH to Auzure CR
#
# 1. Log in to azure: az login
# 2. Log into Azure container registry: az acr login --name wsdotdev  OR  az acr login --name wsdotprod
# 3. Push image: docker push wsdotdev.azurecr.io/sequoia:latest OR docker push wsdotprod.azurecr.io/sequoia:latest
#
# Run Image on Azure
#
# 1. Got to app services portal page
# 2. Stop and restart app


# Base Image
FROM python:3.9

# create and set working directory
RUN mkdir -p /home/gtfs_grading
ENV APP_HOME=/home/gtfs_grading/web
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/staticfiles
WORKDIR $APP_HOME

COPY ./entrypoint.sh $APP_HOME

# Add current directory code to working directory
ADD . $APP_HOME


# set default environment variables
ENV PYTHONUNBUFFERED 1
ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive

# set project environment variables
# grab these via Python's os.environ
# these are 100% optional here
ENV PORT=8000

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3-setuptools \
        python3-pip \
        python3-dev \
        python3-venv \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


# install environment dependencies
RUN pip3 install --upgrade pip
RUN pip3 install pipenv

# Install project dependencies
#RUN pipenv install --skip-lock --system --dev
RUN pip install -r requirements.txt
EXPOSE 8888

ENTRYPOINT ["/home/gtfs_grading/web/entrypoint.sh"]
