#!/bin/sh

#Docker image
docker_name="flextesa_sandbox"
flextesa_image="registry.gitlab.com/tezos/flextesa:00b415f2-run"
port=20000


#Instantation Dockerfile
docker run --rm --name $docker_name -e block_time=1 --detach -p $port:$port $flextesa_image delphibox start
