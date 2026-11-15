FROM lab-base-net
# ShellCheck, for the check that the learner's script is clean. The base
# doesn't carry it, so it is a layer of this lab's own: the same line,
# straight after FROM, in every Module 3 network lab that lints a script, so
# Docker builds it once for all of them.
RUN apt-get update  && apt-get install -y --no-install-recommends shellcheck  && rm -rf /var/lib/apt/lists/*
# The cables and addresses, srv's and far's firewalls and web servers, and
# the checks' test of the learner's script, which builds throwaway machines
# of its own at check time.
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
COPY why-not-cases /usr/local/lib/lab/why-not-cases
# A page for srv's and far's web servers (each machine's nginx serves
# /srv/www). Then every machine gets its own copy of what its services
# need, and the cables are sealed as scenery.
RUN chmod 755 /usr/local/lib/lab/why-not-cases \
 && mkdir -p /srv/www \
 && echo "a web server" > /srv/www/index.html \
 && netlab enable \
 && netlab seal /etc/netlab/topology
