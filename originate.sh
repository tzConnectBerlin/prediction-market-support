#!/bin/bash

ligo compile-contract wolfram.mligo main > wolfram.tz || true

. ./bash-ini-parser.sh

cfg_parser 'oracle.ini'
cfg_section_Tezos

tezos-client -A $node -P $port originate contract wolfram transferring 2 from $owner running wolfram.tz --init "`./initial-storage.sh`"  --burn-cap 0.25525 --force
