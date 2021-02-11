#!/bin/sh

nginx
mkdir -p /etc/nginx/html/
while true; do
    python3 /usr/src/app/cache.py > markets.json
    mv markets.json /etc/nginx/html/markets.json
    python3 /usr/src/app/stablecoin-balances.py > stablecoin-balances.json
    mv stablecoin-balances.json /etc/nginx/html/stablecoin-balances.json
    python3 /usr/src/app/ledger-balances.py > ledger-balances.json
    mv ledger-balances.json /etc/nginx/html/ledger-balances.json
    sleep 10
done
