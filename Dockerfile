# ffmpeg - http://ffmpeg.org/download.html
#
# https://hub.docker.com/r/jrottenberg/ffmpeg/
#
#

FROM        jrottenberg/ffmpeg:3.4-alpine AS base

#install python3.6
RUN apk add --no-cache python3 && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
    rm -r /root/.cache

# Add vod
FROM base AS release
WORKDIR /app

COPY requirements.txt /app/

RUN apk add --no-cache \
  --virtual=.build-dependencies \
  build-base python3-dev file && \
  apk add --no-cache jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev \
  tiff-dev tk-dev tcl-dev && \
  apk add tzdata && \
  ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \ 
  echo "Asia/Shanghai" > /etc/timezone && \
  ln -s locale.h /usr/include/xlocale.h && \
  pip install -r /app/requirements.txt && \
  rm -r /root/.cache && \
  find /usr/lib/python3.*/ -name 'tests' -exec rm -r '{}' + && \
  find /usr/lib/python3.*/site-packages/ -name '*.so' -print -exec sh -c 'file "{}" | grep -q "not stripped" && strip -s "{}"' \; && \
  rm /usr/include/xlocale.h && \
  apk del .build-dependencies 


RUN ln -s /bin/sh /bin/bash

ENV DJANGO_PORT=8000 \
  DJANGO_LOG=$PWD \
  DJANGO_DB_HOST=vod_db \
  TSRTMP_DB_HOST=vod_db \
  LOG_DIR=logs \
  ERROR_LOG=error.log 
RUN apk add --no-cache curl
HEALTHCHECK --interval=30s --timeout=3s CMD curl -fs http://localhost:$DJANGO_PORT/admin || exit 1

COPY . /app

EXPOSE 8000
ENTRYPOINT [ "" ]

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
