FROM ubuntu:24.04
# A plain lab (no systemd, no network of machines): the learner's script is
# the subject. The first RUN is Module 3's plain line, the same in every
# plain lab, so Docker builds that layer once (content/README.md, "Network
# labs"). Python is the checks' tool and the practice issuer's, never the
# learner's. ShellCheck, for the check that the script is clean, is a second
# layer, the same as Routing's write lab's; jq, which the script reads JSON
# with, is this lab's own third.
RUN apt-get update \
 && apt-get install -y --no-install-recommends sudo nano less python3 ipcalc sipcalc openssl curl \
 && rm -rf /var/lib/apt/lists/* \
 && useradd -m -s /bin/bash learner \
 && echo 'learner ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/learner \
 && chmod 440 /etc/sudoers.d/learner
RUN apt-get update \
 && apt-get install -y --no-install-recommends shellcheck \
 && rm -rf /var/lib/apt/lists/*
RUN apt-get update \
 && apt-get install -y --no-install-recommends jq \
 && rm -rf /var/lib/apt/lists/*

# The practice issuer and the checks' cases (token-cases makes tokens; it
# never judges one), the command that starts the issuer with the lab, and
# sample-token, which hands the learner a token to try.
COPY token-cases start /usr/local/lib/lab/
COPY sample-token /usr/local/bin/sample-token
RUN chmod 755 /usr/local/lib/lab/token-cases /usr/local/lib/lab/start /usr/local/bin/sample-token \
 && install -d -o learner -g learner /home/learner/bin /var/lib/lab/issuer

USER learner
WORKDIR /home/learner
CMD ["/usr/local/lib/lab/start"]
