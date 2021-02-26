#!/bin/sh

#Docker image
docker_name="flextesa-sandbox"
flextesa_image="registry.gitlab.com/tezos/flextesa:51670095-run"
port=20000


#Instantation Dockerfile
docker run --rm --name $docker_name -e block_time=1 --detach -p $port:$port $flextesa_image flextesa key bob
docker run --rm --name $docker_name -e block_time=1 -p $port:$port $flextesa_image edobox start
