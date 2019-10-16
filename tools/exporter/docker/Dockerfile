FROM       python:3.7.4-buster
ENV        format="sql"
RUN        apt-get update \
                && apt-get install -y curl apt-transport-https gnupg2 \
                && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
                && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list \
                && apt-get update \
                && ACCEPT_EULA=Y apt-get install -y msodbcsql17 mssql-tools
RUN        apt-get install -y \
           libffi6 \
           libffi-dev \
           git \
           libssl-dev \
           libxml2-dev \
           libxslt-dev \
           unixodbc-dev
COPY       . /app
WORKDIR    /app
RUN        git clone --single-branch --branch beta https://github.com/SafetyCulture/safetyculture-sdk-python/
WORKDIR    /app/safetyculture-sdk-python
RUN        pip install --user .
WORKDIR    /app/safetyculture-sdk-python/tools/exporter
RUN        pip install -r requirements.txt
ENTRYPOINT python exporter.py --loop --format $format
