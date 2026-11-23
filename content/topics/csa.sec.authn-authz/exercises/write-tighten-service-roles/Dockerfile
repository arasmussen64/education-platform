FROM lab-base-policy
# A plain lab on the policy base (content/lab-bases/policy/README.md): the
# base ends as the learner, so the lab's own files go in as root and the
# last line hands back.
USER root

# The operations schema, accounts, catalogue and job descriptions
# (read-only: the system as it is) and the policy file, which is the
# learner's; the access log, written at build by seed.sh from a loop
# counter; the checks' own case generator, with the checksums of the files
# that must stay as they are, out of the learner's PATH.
COPY ops/ /home/learner/ops/
COPY seed.sh /usr/local/lib/lab/seed.sh
COPY ops-cases /usr/local/lib/lab-checks/ops-cases
RUN chmod 755 /usr/local/lib/lab-checks/ops-cases \
 && bash /usr/local/lib/lab/seed.sh \
 && rm -r /usr/local/lib/lab \
 && chmod -R a+rX,go-w /home/learner/ops \
 && chown learner:learner /home/learner/ops /home/learner/ops/policies.cedar \
 && sha256sum /home/learner/ops/ops.cedarschema /home/learner/ops/entities.json /home/learner/ops/catalogue.txt /home/learner/ops/jobs.txt /home/learner/ops/log /var/log/ops/access.log > /usr/local/lib/lab-checks/ops.sha256

USER learner
