#!/bin/sh

set -e

tezos-client -A tezos.newby.org transfer 0 from alice to wolfram --arg "`./compile-ask-parameter.sh`" --burn-cap 0.03925
