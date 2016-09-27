#!/bin/sh

name=gbm-nginx

if docker ps -a -q --filter="name=$name"; then
  docker stop "$name" && docker rm -f "$name"
fi

docker pull registry.gitlab.com/yannhowe/$name:staging
docker run -d --name gbm-nginx -p 80:80  registry.gitlab.com/yannhowe/$name:staging
