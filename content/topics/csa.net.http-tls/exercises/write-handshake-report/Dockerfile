FROM ubuntu:24.04
# A plain lab (no systemd, no network of machines): the learner's script is
# the subject. The first RUN is Module 3's plain line, the same in every
# Module 3 plain lab, so Docker builds that layer once (content/README.md,
# "Network labs"). ShellCheck, for the check that the script is clean, is a
# second layer, the same as Routing's and HTTP semantics' write labs'.
RUN apt-get update \
 && apt-get install -y --no-install-recommends sudo nano less python3 ipcalc sipcalc openssl curl \
 && rm -rf /var/lib/apt/lists/* \
 && useradd -m -s /bin/bash learner \
 && echo 'learner ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/learner \
 && chmod 440 /etc/sudoers.d/learner
RUN apt-get update \
 && apt-get install -y --no-install-recommends shellcheck \
 && rm -rf /var/lib/apt/lists/*

# The helpers that make throwaway TLS servers (the lab's example servers,
# which start runs, and the checks' own), and the checks' comparison.
COPY tls-servers report-cases start /usr/local/lib/lab/
COPY seed.sh /tmp/seed.sh
RUN chmod 755 /usr/local/lib/lab/report-cases /usr/local/lib/lab/start \
 && chmod 644 /usr/local/lib/lab/tls-servers \
 && bash /tmp/seed.sh && rm /tmp/seed.sh

USER learner
WORKDIR /home/learner
CMD ["/usr/local/lib/lab/start"]
