#!/bin/sh

ligo compile-contract wolfram.mligo main > wofram.tz || true

. bash-ini-parser.sh

cfg_parser 'woracle.ini'
cfg_section_Tezos

tezos-client -A $node originate contract wolfram transferring 30 from $owner running wolfram.tz --init "`./initial-storage.sh`"  --burn-cap 0.25525 --force
