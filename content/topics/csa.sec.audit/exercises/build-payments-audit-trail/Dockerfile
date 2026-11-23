FROM lab-base-pay
# The payments server as the base ships it: the audit writer running with a
# policy that records sign-ins only, and an audit journal that isn't
# sealed. The lab adds the folder where the verification key is left for
# the auditors (the lab's stand-in for handing it to people who don't run
# this server) and the checks' own helpers.
COPY trail.sh policy-check /usr/local/lib/lab/
RUN chmod 644 /usr/local/lib/lab/trail.sh \
 && chmod 755 /usr/local/lib/lab/policy-check \
 && mkdir -p /srv/auditors
