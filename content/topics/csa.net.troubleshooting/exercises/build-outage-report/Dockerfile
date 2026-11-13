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

# The office monitor's real log: captured on 2026-11-12 (the lab's clock,
# UTC) in Follow the method's network on the network-lab base, before that
# walkthrough's fix (so loads that tried 10.30.0.11 first were slow), with
# app1's web server stopped from 22:02:56 to 22:03:41; 233 loads. Then the
# checks' own tools, out of the learner's PATH, and the learner's ~/bin.
COPY shop-monitor.log /var/log/shop-monitor.log
COPY make-log report-truth reportcheck.sh /usr/local/lib/lab-checks/
RUN chmod 644 /var/log/shop-monitor.log /usr/local/lib/lab-checks/reportcheck.sh \
 && chmod 755 /usr/local/lib/lab-checks/make-log /usr/local/lib/lab-checks/report-truth \
 && install -d -o learner -g learner /home/learner/bin

USER learner
WORKDIR /home/learner
CMD ["sleep", "infinity"]
