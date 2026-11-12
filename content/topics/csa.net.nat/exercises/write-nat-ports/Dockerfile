FROM ubuntu:24.04
# A plain lab (no systemd, no network): the learner's script is the
# subject. The first RUN is Module 3's plain line, the same in every Module 3
# plain lab, so Docker builds that layer once (content/README.md, "Network
# labs"). Python is the checks' tool, never the learner's. ShellCheck, for
# the check that the script is clean, is a second layer, as in Routing's
# write lab.
RUN apt-get update \
 && apt-get install -y --no-install-recommends sudo nano less python3 ipcalc sipcalc openssl curl \
 && rm -rf /var/lib/apt/lists/* \
 && useradd -m -s /bin/bash learner \
 && echo 'learner ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/learner \
 && chmod 440 /etc/sudoers.d/learner
RUN apt-get update \
 && apt-get install -y --no-install-recommends shellcheck \
 && rm -rf /var/lib/apt/lists/*

# The checks' own answer (nat-truth), and a listing to try the script on.
COPY nat-truth /usr/local/lib/lab/nat-truth
COPY seed.sh /tmp/seed.sh
RUN chmod 755 /usr/local/lib/lab/nat-truth && bash /tmp/seed.sh && rm /tmp/seed.sh

USER learner
WORKDIR /home/learner
CMD ["sleep", "infinity"]
