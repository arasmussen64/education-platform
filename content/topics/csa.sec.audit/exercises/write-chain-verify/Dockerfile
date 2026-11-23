FROM ubuntu:24.04
# A plain lab (no systemd, no server): the learner's script is the subject.
# The first RUN is Module 3's plain line, the same in every plain lab since
# then, so Docker builds that layer once (content/README.md, "Network
# labs"). sha256sum, cut and printf are in every Ubuntu image.
RUN apt-get update \
 && apt-get install -y --no-install-recommends sudo nano less python3 ipcalc sipcalc openssl curl \
 && rm -rf /var/lib/apt/lists/* \
 && useradd -m -s /bin/bash learner \
 && echo 'learner ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/learner \
 && chmod 440 /etc/sudoers.d/learner

# The checks' own program (it makes logs as a check runs, tampers with
# them, and works out the right verdict with Python), and the scenery:
# chain-add and five example logs.
COPY chain-cases /usr/local/lib/lab/chain-cases
COPY seed.sh /tmp/seed.sh
RUN chmod 755 /usr/local/lib/lab/chain-cases \
 && bash /tmp/seed.sh && rm /tmp/seed.sh

USER learner
WORKDIR /home/learner
CMD ["sleep", "infinity"]
