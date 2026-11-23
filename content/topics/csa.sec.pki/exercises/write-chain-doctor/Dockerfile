FROM ubuntu:24.04
# A plain lab (no systemd, no network of machines): the learner's script is
# the subject. The first RUN is Module 3's plain line, the same in every
# plain lab that uses it, so Docker builds that layer once (content/README.md,
# "Network labs"). ShellCheck, for the check that the script is clean, is a
# second layer, the same as Module 3's write labs'.
RUN apt-get update \
 && apt-get install -y --no-install-recommends sudo nano less python3 ipcalc sipcalc openssl curl \
 && rm -rf /var/lib/apt/lists/* \
 && useradd -m -s /bin/bash learner \
 && echo 'learner ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/learner \
 && chmod 440 /etc/sudoers.d/learner
RUN apt-get update \
 && apt-get install -y --no-install-recommends shellcheck \
 && rm -rf /var/lib/apt/lists/*

# The helpers that make small certificate authorities and one case of each
# kind (the lab's examples, made here, and the checks' own, made as they
# run), and the checks' comparison. The folder is closed to the learner's
# account once the examples are made: what a case should give is the
# checks' business.
COPY pki-cases make-case chain-cases /usr/local/lib/lab/
COPY seed.sh /tmp/seed.sh
RUN chmod 755 /usr/local/lib/lab/make-case /usr/local/lib/lab/chain-cases \
 && chmod 644 /usr/local/lib/lab/pki-cases \
 && bash /tmp/seed.sh && rm /tmp/seed.sh

USER learner
WORKDIR /home/learner
CMD ["sleep", "infinity"]
