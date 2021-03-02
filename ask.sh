#!/bin/bash

. ./bash-ini-parser.sh

cfg_parser 'oracle.ini'
cfg_section_Tezos

tezos-client -A $endpoint -P $port transfer 0 from alice to wolfram --arg "`./compile-ask-parameter.sh`" --burn-cap 0.03925
