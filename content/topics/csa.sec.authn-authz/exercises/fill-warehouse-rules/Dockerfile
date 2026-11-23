FROM lab-base-policy
# A plain lab on the policy base (content/lab-bases/policy/README.md): the
# base ends as the learner, so the lab's own files go in as root and the
# last line hands back.
USER root

# The warehouse's schema and people (read-only: the system as it is) and
# the policy file with its four gaps, which is the learner's; the checks'
# own case generator, with the checksums of the files that must stay as
# they are, out of the learner's PATH.
COPY warehouse/ /home/learner/warehouse/
COPY warehouse-cases /usr/local/lib/lab-checks/warehouse-cases
RUN chmod 755 /usr/local/lib/lab-checks/warehouse-cases \
 && chmod -R a+rX,go-w /home/learner/warehouse \
 && chown learner:learner /home/learner/warehouse /home/learner/warehouse/policies.cedar \
 && sha256sum /home/learner/warehouse/warehouse.cedarschema /home/learner/warehouse/entities.json > /usr/local/lib/lab-checks/warehouse.sha256

USER learner
