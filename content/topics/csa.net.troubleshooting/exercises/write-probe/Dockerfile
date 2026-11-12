FROM lab-base-net
# The network (the office and targets) and targets' own files: its name
# server and its web server.
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
# The checks' own throwaway servers and helpers, out of the learner's PATH.
COPY scenery/kth-server scenery/hangup-server scenery/probecheck.sh /usr/local/lib/lab/
# The learner's ~/bin, for the probe; every machine gets its own copy of
# what its services need and they start at every boot; and the network and
# targets' files are sealed.
RUN chmod 755 /usr/local/lib/lab/kth-server /usr/local/lib/lab/hangup-server \
 && chmod 644 /usr/local/lib/lab/probecheck.sh \
 && install -d -o learner -g learner /home/learner/bin \
 && netlab enable \
 && netlab seal /etc/netlab/topology /etc/netns/targets/unbound/unbound.conf /etc/netns/targets/nginx/sites-enabled/default
