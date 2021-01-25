#!/bin/sh

KEY=`grep -A5 '\[Tezos\]' woracle.ini |grep owner | sed -e 's/owner = //'`

ligo compile-storage wolfram.mligo main "{ questions = (Map.empty :  (string, query_storage) map) ; owner = (\"$KEY\" : address) }"
