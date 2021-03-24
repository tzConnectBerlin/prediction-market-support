FROM python:3.9-slim-buster

RUN mkdir /cli
COPY pyproject.toml poetry.lock /cli/

WORKDIR /cli

ENV PYTHONPATH=${PYTHONPATH}:${PWD}

RUN apt-get update
RUN apt-get -y install libsodium-dev libsecp256k1-dev libgmp-dev git gcc pkg-config wget


RUN pip3 install poetry

RUN poetry config virtualenvs.create false

RUN poetry install --no-dev --no-root

RUN wget -O /cli/tezos-client https://github.com/serokell/tezos-packaging/releases/latest/download/tezos-client
RUN chmod +x tezos-client
RUN mv tezos-client /usr/bin


COPY . /cli


CMD ["bash"]
