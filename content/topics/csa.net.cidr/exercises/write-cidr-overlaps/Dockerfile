FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive

# A plain lab (no systemd): a bash script is the subject. The first RUN is
# the one every Module 3 plain lab shares (content/README.md, "Network
# labs"), so Docker builds it once for all of them; Python is the checks'
# tool, not the learner's.
RUN apt-get update \
 && apt-get install -y --no-install-recommends sudo nano less python3 ipcalc sipcalc openssl curl \
 && rm -rf /var/lib/apt/lists/* \
 && useradd -m -s /bin/bash learner \
 && echo 'learner ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/learner \
 && chmod 440 /etc/sudoers.d/learner

# This topic's plain labs lint the learner's scripts too: the same second
# RUN in each of them.
RUN apt-get update \
 && apt-get install -y --no-install-recommends shellcheck \
 && rm -rf /var/lib/apt/lists/*

# The sample plan goes into ~/plans; the checks' helper stays where the
# checks find it.
COPY sites.txt seed.sh /usr/local/lib/lab/
COPY overlaps-truth /usr/local/lib/lab-checks/overlaps-truth
RUN chmod 755 /usr/local/lib/lab-checks/overlaps-truth \
 && bash /usr/local/lib/lab/seed.sh \
 && rm -r /usr/local/lib/lab

USER learner
WORKDIR /home/learner
CMD ["sleep", "infinity"]
