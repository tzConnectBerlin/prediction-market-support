FROM registry.gitlab.com/tezos/flextesa:master-run
RUN apk add tzdata
RUN cp /usr/share/zoneinfo/Europe/Berlin /etc/localtime
RUN echo "Europe/Berlin" > /etc/timezone
COPY test_sandbox.sh .
