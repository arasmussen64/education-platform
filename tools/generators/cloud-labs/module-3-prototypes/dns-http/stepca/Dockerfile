FROM m3proto-dnshttp-tls
ADD https://github.com/smallstep/certificates/releases/download/v0.30.2/step-ca_0.30.2-1_amd64.deb /tmp/
ADD https://github.com/smallstep/cli/releases/download/v0.31.0/step-cli_0.31.0-1_amd64.deb /tmp/
RUN sha256sum /tmp/*.deb && apt-get install -y /tmp/step-cli_0.31.0-1_amd64.deb /tmp/step-ca_0.30.2-1_amd64.deb >/dev/null && rm /tmp/*.deb && step version && step-ca version
