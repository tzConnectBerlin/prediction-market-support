#!/bin/sh

#Docker image
docker_name="flextesa-sandbox"
test_sandbox="test-sandbox"
default_protocol="granabox"
root_path=/tmp/mini-box
flextesa_image="tqtezos/flextesa:20210602"
#flextesa_image="bakingbad/sandboxed-node"
port=20000

#Instantation Dockerfile
#docker run --rm --name $docker_name -e block_time=1 --detach -p $port:$port $flextesa_image flextesa key bob
#docker build -t $flextesa_image  sandbox/
docker run -d --rm --name $docker_name -e block_time=1 -p 20000:20000 $flextesa_image $default_protocol start
