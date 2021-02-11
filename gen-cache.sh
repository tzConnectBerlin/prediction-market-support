#!/bin/sh

. venv/bin/activate

while true; do
    echo -n .
    python3 cache.py  > markets.json
    echo -n .
    mv markets.json ../pmcache.newby.org/markets.json
    echo -n .
    python3 stablecoin-balances.py > stablecoin-balances.json
    echo -n .
    mv stablecoin-balances.json ../pmcache.newby.org/stablecoin-balances.json
    echo -n .
    python3 ledger-balances.py > ledger-balances.json
    echo -n .
    mv ledger-balances.json ../pmcache.newby.org/ledger-balances.json
    sleep 10
    echo "Loop"
done
