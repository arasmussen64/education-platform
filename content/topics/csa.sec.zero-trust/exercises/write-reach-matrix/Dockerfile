FROM lab-base-net
# ShellCheck, for the check that the learner's script is clean. The base
# doesn't carry it, so it is a layer of this lab's own: the same line,
# straight after FROM, in every Module 3 network lab that lints a script, so
# Docker builds it once for all of them.
RUN apt-get update  && apt-get install -y --no-install-recommends shellcheck  && rm -rf /var/lib/apt/lists/*
# The apps network, the three apps' own files, the stand-in database's
# unit, a file of connections to try the script on, and the checks' test of
# the learner's script, which builds throwaway machines of its own at check
# time (root only, so the script can't call it).
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
COPY units/shop-db@.service /etc/systemd/system/
COPY reach-cases /usr/local/lib/lab/reach-cases
COPY apps.txt /home/learner/apps.txt
RUN chmod 700 /usr/local/lib/lab/reach-cases \
 && chmod 644 /etc/systemd/system/shop-db@.service \
 && install -d -o learner -g learner /home/learner/bin \
 && chown learner:learner /home/learner/apps.txt \
 && netlab enable \
 && systemctl enable shop-db@db \
 && netlab seal /etc/netlab/topology
