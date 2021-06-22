#! /bin/sh

default_protocol=Florence

all_commands="
* usage | help | --help | -h: Display this help message."
usage () {
        cat >&2 <<EOF
This script provides a Flextesa “mini-net” sandbox with predefined
parameters useful for tutorials and basic exploration with
wallet software like \`tezos-client\`. This one uses the $default_protocol
protocol.

usage: $0 <command>

where <command> may be:
$all_commands
EOF
}

time_bb=${block_time:-5}

export alice="$(flextesa key alice)"

#Accounts for tests
export siri="siri,edpkuvy4t4TAsMbii31MhE2N3Qh5dMU99yHcdKYU2FrCiNit5DoUrX,tz1MT1ZfNoDXzWvUj4zJg8cVq7tt7a6QcC58,unencrypted:edsk3Q3uoz73R7a2GoKHncLZMGD14rKydkiypCvrN3iXk3Ufmx6ZtR"
export leonidas="leonidas,edpkubySH5X7nj2snpWe51joWyrEtEzVgBxJ4mFxvrDMqQqotm1yNC,tz1ZrWi7V8tu3tVepAQVAEt8jgLz4VVEEf7m,unencrypted:edsk4QvnUzAQ3s8jiFdmpAztGtXkUoKiKJdKS4QeqdM9aZNE53q8FD"
export rimk="rimk,edpkuz9PdqkfWPTxxC1uhTnWtkDsb2hWWKhfj54v3yiPAdhHo6He3E,tz1PMqV7qGgWMNH2HR9inWjSvf3NwtHg7Xg4,unencrypted:edsk3aE3Faxgb2mvjHGSHDW4U9TwrGnuRuamJBCcr1wbqMjR2QtXCV"
export donald="donald,edpktqDLAmhcUAbztjBP7v8fyj5NGWU1G47kZrpvBY19TMLgjFRovR,tz1VWU45MQ7nxu5PGgWxgDePemev6bUDNGZ2,unencrypted:edsk2sRikkzrGKnRC28UhvJsKAM19vuv4LtCRViyjkm2jMyAxiCMuG"
export mala="mala,edpkv9FcnmEx1LET4F9hhKdijvZcj4YynekNQrhbugqAyuqyyzTJFR,tz1azKk3gBJRjW11JAh8J1CBP1tF2NUu5yJ3,unencrypted:edsk4FxpsXkEmFG7fKygaWYJ4hb65vuH55ehM2856xAvipztVWuxJM"
export stavros="stavros,edpkvRf4cKZ3hJJRrProttxwQW2LhHRn3T49pa2MrvSmCiKxc2VQkY,tz1iPFr4obPeSzknBPud8uWXZC7j5gKoah8d,unencrypted:edsk36su9hdbfCCpJnDdCsQVs4JSbf7DcmPbeRBhpZznzEcX5gPRpP"
export marty="marty,edpkuvwKYxfbAN5DLXvHxE3XwWmanfhLQpx3LdH1oF9oB549iS8sCv,tz1Q3eT3kwr1hfvK49HK8YqPadNXzxdxnE7u,unencrypted:edsk4MmZRWF3uzMLh28g4ocxHsJPzLNrKeGTwM5uX3sFDn63GMPiog"

all_commands="$all_commands


* start : Start the sandbox."

root_path=/tmp/mini-box
start () {
        flextesa mini-net \
                --root "$root_path" --size 1 "$@" \
                --set-history-mode N000:archive \
                --time-b "$time_bb" \
                --remove-default-bootstrap-accounts \
                --add-bootstrap-account="$alice@2_000_000_000_000" \
                --add-bootstrap-account="$siri@2_000_000_000_000" \
                --add-bootstrap-account="$leonidas@2_000_000_000_000" \
                --add-bootstrap-account="$rimk@2_000_000_000_000" \
                --add-bootstrap-account="$mala@2_000_000_000_000" \
                --add-bootstrap-account="$donald@2_000_000_000_000" \
                --add-bootstrap-account="$stavros@2_000_000_000_000" \
                --add-bootstrap-account="$marty@2_000_000_000_000" \
                --until-level 200_000_000 \
                --timestamp-delay=-3600 \
                --with-timestamp \
                --no-baking \
                --protocol-kind "$default_protocol"
        }

all_commands="$all_commands
* info : Show accounts and information about the sandbox."
info () {
        cat >&2 <<EOF
Usable accounts:

- $(echo $alice | sed 's/,/\n  * /g')
- $(echo $bob | sed 's/,/\n  * /g')

Root path (logs, chain data, etc.): $root_path (inside container).
EOF
}


if [ "$1" = "" ] || [ "$1" = "help" ] || [ "$1" = "--help" ] || [ "$1" = "-h" ] ; then
        usage
else
        "$@"
fi
