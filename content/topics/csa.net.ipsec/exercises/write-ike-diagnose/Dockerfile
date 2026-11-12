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

# The checks' log maker stays where the checks find it, out of the
# learner's PATH. Three sample logs, made by it from fixed seeds, go into
# ~/logs for the learner to try the script on, and ~/bin waits for it.
COPY ike-log /usr/local/lib/lab-checks/ike-log
RUN chmod 755 /usr/local/lib/lab-checks/ike-log \
 && mkdir -p /home/learner/bin /home/learner/logs \
 && /usr/local/lib/lab-checks/ike-log esp-proposal --seed 11 > /home/learner/logs/monday.log \
 && /usr/local/lib/lab-checks/ike-log auth --seed 23 > /home/learner/logs/tuesday.log \
 && /usr/local/lib/lab-checks/ike-log rekey --seed 37 > /home/learner/logs/wednesday.log \
 && chown -R learner:learner /home/learner/bin /home/learner/logs

USER learner
WORKDIR /home/learner
CMD ["sleep", "infinity"]
