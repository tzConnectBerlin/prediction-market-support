#!/bin/sh

#Docker image
export flextesa_image=registry.gitlab.com/tezos/flextesa:image-tutobox-run

#Instantation Dockerfile
docker run --rm --name flextesa-sandbox -e block_time=1 --detach -p 20000:20000 tqtezos/flextesa:20200925 delphibox start
