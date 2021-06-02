#!/bin/sh

#Docker image
docker_name="flextesa-sandbox"
test_sandbox="test-sandbox"
default_protocol="edobox"
root_path=/tmp/mini-box
flextesa_image="registry.gitlab.com/tezos/flextesa:51670095-run"
port=20001
alice=docker run --rm --name $docker_name -e block_time=1 --detach -p $port:$port $flextesa_image flextesa key alice
bob=docker run --rm --name $docker_name -e block_time=1 --detach -p $port:$port $flextesa_image flextesa key bob
command=flextesa mini-net \
             --root "$root_path" --size 1 "$@" \
             --set-history-mode N000:archive \
             --number-of-b 1 \
             --time-b "0" \
             --add-bootstrap-account="$alice@2_000_000_000_000" \
             --add-bootstrap-account="$bob@2_000_000_000_000" \
             --no-daemons-for=alice \
             --no-daemons-for=bob \
             --until-level 200_000_000 \
             --protocol-kind "$default_protocol"


#Instantation Dockerfile
#docker run --rm --name $docker_name -e block_time=1 --detach -p $port:$port $flextesa_image flextesa key bob
#docker run --rm --name $docker_name -e block_time=1 --detach -p $port:$port $flextesa_image edobox start
docker run --rm --name $test_sandbox --detach -p $port:$port $flextesa_image $command 
