FROM ubuntu:24.04
# A plain lab (no systemd, no network): the learner's script is the
# subject. The first RUN is Module 3's plain line, the same in every Module 3
# plain lab, so Docker builds that layer once (content/README.md, "Network
# labs"). Python is the checks' tool, never the learner's. ShellCheck, for
# the check that the script is clean, is this topic's own second layer.
RUN apt-get update \
 && apt-get install -y --no-install-recommends sudo nano less python3 ipcalc sipcalc openssl curl \
 && rm -rf /var/lib/apt/lists/* \
 && useradd -m -s /bin/bash learner \
 && echo 'learner ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/learner \
 && chmod 440 /etc/sudoers.d/learner
RUN apt-get update \
 && apt-get install -y --no-install-recommends shellcheck \
 && rm -rf /var/lib/apt/lists/*

# The checks' own answer (route-truth), and a table to try the script on.
COPY route-truth /usr/local/lib/lab/route-truth
COPY seed.sh /tmp/seed.sh
RUN chmod 755 /usr/local/lib/lab/route-truth && bash /tmp/seed.sh && rm /tmp/seed.sh

USER learner
WORKDIR /home/learner
CMD ["sleep", "infinity"]
