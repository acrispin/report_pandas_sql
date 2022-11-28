FROM python:3.11.0-slim-bullseye AS base
#FROM python:3.10.8-slim-bullseye AS base

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update -y && apt-get install -y gnupg curl \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update -y \
    && ACCEPT_EULA=Y apt-get install msodbcsql18 -y \
    && ACCEPT_EULA=Y apt-get install mssql-tools18 -y \
    && echo 'export PATH="$PATH:/opt/mssql-tools18/bin"' >> ~/.bash_profile \
    && echo 'export PATH="$PATH:/opt/mssql-tools18/bin"' >> ~/.bashrc \
    && /bin/bash -c "source ~/.bashrc"

RUN apt-get install -y dumb-init \
    && apt-get install unixodbc-dev -y \
    && apt-get install libgssapi-krb5-2 -y \
    && apt-get install g++ -y

#RUN apt-get update -yqq \
#    && apt-get install -y --no-install-recommends openssl \
#    && sed -i 's,^\(MinProtocol[ ]*=\).*,\1'TLSv1',g' /etc/ssl/openssl.cnf \
#    && sed -i 's,^\(CipherString[ ]*=\).*,\1'DEFAULT@SECLEVEL=1',g' /etc/ssl/openssl.cnf \
#    && rm -rf /var/lib/apt/lists/* \

# FIX CVE-2022-2509, CVE-2021-46828
RUN apt-get update -y && apt-get --only-upgrade install libgnutls30 libtirpc3 libtirpc-common -y

RUN pip install --upgrade pip


FROM base AS release

COPY ./requirements-docker.txt /app/requirements.txt
RUN pip --no-cache-dir install -r /app/requirements.txt

# COPY ./src/*.py /app/src/
# COPY ./main.py /app/main.py
COPY ./base.ipynb /app/base.ipynb

ENV APP_DIR=/app
WORKDIR $APP_DIR

ARG APP_USER=jupyteruser
RUN groupadd -r $APP_USER && useradd -m -s /bin/false -g $APP_USER $APP_USER
RUN chown -R $APP_USER:$APP_USER $APP_DIR
USER $APP_USER
# RUN chmod 777 -R /home/$APP_USER

# Make port 8888 available to the world outside this container
EXPOSE 8888

# Create mountpoint
VOLUME $APP_DIR

# Run jupyter when container launches
CMD ["jupyter", "notebook", "--ip='*'", "--port=8888", "--no-browser", "--allow-root"]
