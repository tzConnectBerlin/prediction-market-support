#!/bin/sh
tezos-client -E $ENDPOINT transfer 0 from $ACCOUNT to $CONTRACT --arg "(Left (Left (Left (Left (Pair \"$AUCTION\" (Pair $RATE $QUANTITY))))))" --burn-cap 0.04 > /dev/null && echo "Success"
