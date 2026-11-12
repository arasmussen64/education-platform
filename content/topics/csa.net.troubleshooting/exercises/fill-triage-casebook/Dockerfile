FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive

# A plain lab (no systemd): the cases are files to read. The first RUN is the
# one every Module 3 plain lab shares (content/README.md, "Network labs"), so
# Docker builds it once for all of them; Python is the checks' tool, not the
# learner's.
RUN apt-get update \
 && apt-get install -y --no-install-recommends sudo nano less python3 ipcalc sipcalc openssl curl \
 && rm -rf /var/lib/apt/lists/* \
 && useradd -m -s /bin/bash learner \
 && echo 'learner ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/learner \
 && chmod 440 /etc/sudoers.d/learner

# The six cases (read-only), the sheet to fill in, and the checks' own tool
# with the cases' checksums, out of the learner's PATH.
COPY cases/ /srv/cases/
COPY --chown=learner:learner triage.txt /home/learner/triage.txt
COPY triage-check /usr/local/lib/lab-checks/triage-check
RUN chmod -R a+rX,go-w /srv/cases \
 && chmod 755 /usr/local/lib/lab-checks/triage-check \
 && find /srv/cases -type f | sort | xargs sha256sum > /usr/local/lib/lab-checks/cases.sha256

USER learner
WORKDIR /home/learner
CMD ["sleep", "infinity"]
