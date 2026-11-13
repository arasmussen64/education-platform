FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive

# A plain lab (no systemd): an address plan is the subject. The first RUN is
# the one every Module 3 plain lab shares (content/README.md, "Network
# labs"), so Docker builds it once for all of them; Python is the checks'
# tool, not the learner's.
RUN apt-get update \
 && apt-get install -y --no-install-recommends sudo nano less python3 ipcalc sipcalc openssl curl \
 && rm -rf /var/lib/apt/lists/* \
 && useradd -m -s /bin/bash learner \
 && echo 'learner ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/learner \
 && chmod 440 /etc/sudoers.d/learner

# The shop's requirements in /srv/plan (README.txt, sites.csv,
# policy.txt), the learner's plan to fill in, plan-show, and the checks'
# helper, plancheck, where the checks find it and out of the learner's
# PATH. The requirements' checksum is kept for the check that they are
# untouched. Every address-plan lab of this checkpoint has this Dockerfile;
# only the files differ.
COPY plan/ /srv/plan/
COPY plancheck /usr/local/lib/lab-checks/plancheck
COPY plan-show /usr/local/bin/plan-show
COPY starter.csv /home/learner/plan/plan.csv
RUN chmod 755 /usr/local/lib/lab-checks/plancheck /usr/local/bin/plan-show \
 && chmod 755 /srv/plan && chmod 644 /srv/plan/* \
 && chown -R learner:learner /home/learner/plan \
 && (cd /srv/plan && find . -type f | sort | xargs sha256sum | sha256sum | cut -d' ' -f1) > /usr/local/lib/lab-checks/plan.sha256

USER learner
WORKDIR /home/learner
CMD ["sleep", "infinity"]
