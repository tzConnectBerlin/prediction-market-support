#!/bin/sh

IPFS_HASH=Qmf4rFNPH2i29oThjgBg3VeYVnZ3rofiSTRZHaM6vYkZ4Q
TIMESTAMP=`date -u +"%Y-%m-%dt%H:%M:00Z"`

ligo compile-parameter wolfram.mligo main "Ask (\"$IPFS_HASH\", (\"$TIMESTAMP\": timestamp), \"$IPFS_HASH\")"
