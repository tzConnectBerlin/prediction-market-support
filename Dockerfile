FROM nginx:1.19.6
RUN apt-get update && apt-get install -y --no-install-recommends \
  python3 \
  python3-pip \
  pkg-config \
  build-essential \
  autoconf \
  python3-dev \
  && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip3 install --upgrade pip
RUN pip3 install setuptools
RUN pip3 install --no-cache-dir -r requirements.txt
COPY ./docker/nginx.conf /etc/nginx/nginx.conf	
COPY ./docker/nginx-mime.types /etc/nginx/mime.types
COPY ./docker/default.conf /etc/nginx/conf.d/default.conf
COPY . .
CMD [ "/bin/sh", "-c", "/usr/src/app/docker/gen-cache.sh"]
