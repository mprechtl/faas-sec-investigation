# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.7-slim

# Some environment variables
ENV APP_HOME /home/function
ENV GROUP_ID 1000
ENV USER_ID 1000

# create new user and group to the specified ids
RUN groupadd -g ${GROUP_ID} function && \
    useradd -l -u ${USER_ID} -g function function && \
    install -d -m 0755 -o function -g function ${APP_HOME} && \
    chown --changes --silent --no-dereference --recursive ${USER_ID}:${GROUP_ID} ${APP_HOME}

# Copy function code to the container image
WORKDIR $APP_HOME
COPY . ./

USER function

# Install production dependencies.
RUN pip install Flask gunicorn

# Add flask and gunicorn to PATH variable
ENV PATH="/home/function/.local/bin:${PATH}"

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
CMD gunicorn --bind :$PORT --workers 1 --threads 8 app:app
