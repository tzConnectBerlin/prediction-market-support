apk add rsync git m4 alpine-sdk patch unzip wget pkgconfig gmp-dev libev-dev hidapi-dev libffi-dev opam jq
# [install rust]
wget https://sh.rustup.rs/rustup-init.sh
chmod +x rustup-init.sh
./rustup-init.sh --profile minimal --default-toolchain 1.44.0 -y
# [source cargo]
source $HOME/.cargo/env
# [get sources]
git clone https://gitlab.com/tezos/tezos.git
cd tezos
git checkout latest-release
# [install Tezos dependencies]
opam init --bare --disable-sandboxing
# [compile sources]
eval $(opam env)
make build-deps
eval $(opam env)
make
# [optional setup]
export PATH=~/tezos:$PATH
export TEZOS_CLIENT_UNSAFE_DISABLE_DISCLAIMER=Y
