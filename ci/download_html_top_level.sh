#!/bin/bash -ex


echo download top level html

for SPEED in 'fast' 'slow'; do
  pwd
  echo execute ${SPEED}
  wget --no-directories \
       --no-host-directories \
       --page-requisites \
       --adjust-extension \
       --no-cache \
       --no-cookies \
       --directory-prefix=${SPEED} \
       --default-page=index.html \
       "localhost?speed=${SPEED}"
  mv -v "${SPEED}/index.html?speed=${SPEED}.html" ${SPEED}/index.html
  sleep 1
done
