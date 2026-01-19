FROM python:3.11-slim as Base

# Install cron
RUN apt-get update && apt-get install -y cron

WORKDIR /app
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt || true
RUN pip install --no-cache-dir pytest requests mysql-connector-python

# Create cron job (every 12 hours at 00:00 and 12:00)
# RUN echo "* * * * * /usr/local/bin/python3 /app/dockerAutoFile.py >> /var/log/cron.log 2>&1" > /etc/cron.d/mobypark-cron
RUN echo "0 */12 * * * /usr/local/bin/python3 /app/dockerAutoFile.py >> /var/log/cron.log 2>&1" > /etc/cron.d/mobypark-cron
RUN chmod 0644 /etc/cron.d/mobypark-cron
RUN crontab /etc/cron.d/mobypark-cron

# Make log file exist
RUN touch /var/log/cron.log

# Start cron + server
CMD cron && python -u server.py

# Auto test
FROM Base AS test
CMD ["pytest", "tests"]
