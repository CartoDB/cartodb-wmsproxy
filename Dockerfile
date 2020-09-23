FROM httpd:2

RUN apt-get update
RUN apt-get install -y proj-bin python-pip libapr1 libapr1-dev libaprutil1-dev
# RUN pip install meinheld gunicorn

COPY resources/mod_wsgi-4.7.1.tar.gz .
RUN tar xvfz mod_wsgi-4.7.1.tar.gz \
  && cd mod_wsgi-4.7.1 \
  && ./configure \
  && make \
  && make install

RUN useradd -ms /bin/bash mapproxy
USER mapproxy

WORKDIR /home/mapproxy

RUN mkdir logs

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY wmsproxy .
COPY setup.py .

RUN pip install .

COPY resources/mapproxy /etc/mapproxy
COPY resources/mapproxy.conf /usr/local/apache2/conf/httpd.conf

USER root
RUN chown -R mapproxy /etc/mapproxy
ENV APACHE_LOG_DIR /home/mapproxy/logs