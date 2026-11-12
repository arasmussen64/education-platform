FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-cache policy frr frr-pythontools && apt-cache show frr | grep -E '^(Version|Installed-Size|Depends)' | head -5
