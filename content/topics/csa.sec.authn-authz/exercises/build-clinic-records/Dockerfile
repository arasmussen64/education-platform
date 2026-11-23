FROM lab-base-policy
# A plain lab on the policy base (content/lab-bases/policy/README.md): the
# base ends as the learner, so the lab's own files go in as root and the
# last line hands back.
USER root

# The clinic's schema and people (read-only: the system as it is) and the
# empty policy file, which is the learner's; the checks' own case
# generator, with the checksums of the files that must stay as they are,
# out of the learner's PATH.
COPY clinic/ /home/learner/clinic/
COPY clinic-cases /usr/local/lib/lab-checks/clinic-cases
RUN chmod 755 /usr/local/lib/lab-checks/clinic-cases \
 && chmod -R a+rX,go-w /home/learner/clinic \
 && chown learner:learner /home/learner/clinic /home/learner/clinic/policies.cedar \
 && sha256sum /home/learner/clinic/clinic.cedarschema /home/learner/clinic/entities.json > /usr/local/lib/lab-checks/clinic.sha256

USER learner
