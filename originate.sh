#!/bin/sh

set -e

ligo compile-contract wolfram.mligo main > wolfram.tz

NODE=` grep -A5 '\[Tezos\]' woracle.ini |grep node | sed -Ee 's/node *= *//'`
KEY=`grep -A5 -E '\[Tezos\]' woracle.ini |grep owner | sed -e 's/owner *= *//'`

tezos-client -A $NODE originate contract wolfram transferring 30 from $KEY running wolfram.tz --init "`./initial-storage.sh`"  --burn-cap 0.25525 --force
