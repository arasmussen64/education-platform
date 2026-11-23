FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive

# A plain lab (no systemd, no server): the learner's script is the subject.
# The first RUN is the one every plain lab since Module 3 shares
# (content/README.md, "Network labs"), so Docker builds it once for all of
# them; Python is the checks' tool, not the learner's.
RUN apt-get update \
 && apt-get install -y --no-install-recommends sudo nano less python3 ipcalc sipcalc openssl curl \
 && rm -rf /var/lib/apt/lists/* \
 && useradd -m -s /bin/bash learner \
 && echo 'learner ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/learner \
 && chmod 440 /etc/sudoers.d/learner

# A small week to try the script on goes into ~/week; the checks' helper,
# which makes up findings, assets and a policy of its own each time it runs,
# stays where the checks find it.
COPY policy.tsv seed.sh /usr/local/lib/lab/
COPY sla-cases /usr/local/lib/lab-checks/sla-cases
RUN chmod 755 /usr/local/lib/lab-checks/sla-cases \
 && bash /usr/local/lib/lab/seed.sh \
 && rm -r /usr/local/lib/lab

USER learner
WORKDIR /home/learner
CMD ["sleep", "infinity"]
