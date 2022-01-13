#FROM python:3.9.5 AS base
FROM python:3.9.5

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update -y \
    && apt-get install -y dumb-init \
    && ACCEPT_EULA=Y apt-get install msodbcsql17 -y \
    && ACCEPT_EULA=Y apt-get install mssql-tools -y \
    && echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bash_profile \
    && echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc \
    && /bin/bash -c "source ~/.bashrc" \
    && apt-get install unixodbc-dev -y \
    && apt-get install libgssapi-krb5-2 -y
RUN apt-get update -yqq \
    && apt-get install -y --no-install-recommends openssl \
    && sed -i 's,^\(MinProtocol[ ]*=\).*,\1'TLSv1',g' /etc/ssl/openssl.cnf \
    && sed -i 's,^\(CipherString[ ]*=\).*,\1'DEFAULT@SECLEVEL=1',g' /etc/ssl/openssl.cnf\
    && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip


#FROM base AS release

COPY ./requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY ./src/*.py /app/src/
COPY ./main.py /app/main.py

WORKDIR /app/

ARG APP_USER=uniconjob
RUN groupadd -r $APP_USER && useradd -r -s /bin/false -g $APP_USER $APP_USER
RUN chown -R $APP_USER:$APP_USER /app
USER $APP_USER
