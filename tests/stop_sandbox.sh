#!/bin/sh

#Docker image
docker_name="flextesa-sandbox"
flextesa_image="registry.gitlab.com/tezos/flextesa:51670095-run"
port=20000


#Instantation Dockerfile
docker stop $docker_name
