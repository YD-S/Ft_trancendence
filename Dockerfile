FROM python:3.12-bullseye

# Install dependencies
RUN apt-get update && apt-get install -y netcat-traditional nginx

# Set the working directory
WORKDIR /app

# link the current directory to the working directory but not copy the files
VOLUME . /app

COPY backend-entrypoint-dev.sh /tools/backend-entrypoint.sh
COPY requirements.txt /app/requirements.txt

RUN rm /etc/nginx/sites-enabled/default
COPY nginx/server.conf /etc/nginx/sites-enabled/server.conf
COPY nginx/certs /etc/nginx/ssl

# Install dependencies
RUN pip install --break-system-packages -r /app/requirements.txt


# Expose the port
EXPOSE 443

# Run the app
CMD ["/bin/bash", "/tools/backend-entrypoint.sh"]
