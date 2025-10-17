FROM ubuntu:latest
LABEL authors="Nat"

ENTRYPOINT ["top", "-b"]