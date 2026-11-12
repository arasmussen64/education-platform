FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive

# A plain lab (no systemd): the numbers are the subject. The tools for
# reading a machine's processes, CPUs and NUMA nodes, and the learner's
# account with sudo. The first RUN is identical in every plain lab of this
# checkpoint, and in the plain labs of Cores, memory and noisy neighbours,
# so Docker builds this layer once.
RUN apt-get update \
 && apt-get install -y --no-install-recommends sudo nano less procps sysstat numactl \
 && rm -rf /var/lib/apt/lists/* \
 && useradd -m -s /bin/bash learner \
 && echo 'learner ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/learner \
 && chmod 440 /etc/sudoers.d/learner

# The print shop's sizing review: the dated price table, the workloads' briefs and metrics under
# /srv/sizing, metric-summary, and the answers sheet. seed.sh is the same in
# every sizing lab of this checkpoint; the story is its argument.
COPY prices.csv seed.sh /usr/local/lib/lab/
COPY metric-summary /usr/local/bin/metric-summary
RUN chmod 755 /usr/local/bin/metric-summary \
 && bash /usr/local/lib/lab/seed.sh print-shop \
 && rm /usr/local/lib/lab/seed.sh /usr/local/lib/lab/prices.csv

USER learner
WORKDIR /home/learner
CMD ["sleep", "infinity"]
