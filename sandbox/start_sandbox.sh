#!/bin/sh

#Docker image
docker_name="flextesa-sandbox"
test_sandbox="test-sandbox"
default_protocol="edobox"
root_path=/tmp/mini-box
flextesa_image="registry.gitlab.com/tezos/flextesa:51670095-run"
port=20000
alice=docker run --rm --name $docker_name -e block_time=1 --detach -p $port:$port $flextesa_image flextesa key alice
bob=docker run --rm --name $docker_name -e block_time=1 --detach -p $port:$port $flextesa_image flextesa key bob


#Instantation Dockerfile
#docker run --rm --name $docker_name -e block_time=1 --detach -p $port:$port $flextesa_image flextesa key bob
docker run --rm --name $docker_name -e block_time=1 --detach -p $port:$port $flextesa_image edobox start
