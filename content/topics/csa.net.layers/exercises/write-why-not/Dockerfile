FROM lab-base-net
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
