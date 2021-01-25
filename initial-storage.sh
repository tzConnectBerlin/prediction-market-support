#!/bin/sh

. bash-ini-parser.sh

cfg_parser 'woracle.ini'
cfg_section_Tezos

ligo compile-storage wolfram.mligo main "{ questions = (Map.empty :  (string, query_storage) map) ; owner = (\"$owner\" : address) }"
