FROM lab-base-policy
# A plain lab on the policy base (content/lab-bases/policy/README.md): the
# base ends as the learner, so the lab's own files go in as root and the
# last line hands back.
USER root

# The HR portal's schema and people (read-only: the system as it is) and
# its policy file, which is the learner's to repair; the checks' own case
# generator, with the checksums of the files that must stay as they are,
# out of the learner's PATH.
COPY hr/ /home/learner/hr/
COPY hr-cases /usr/local/lib/lab-checks/hr-cases
RUN chmod 755 /usr/local/lib/lab-checks/hr-cases \
 && chmod -R a+rX,go-w /home/learner/hr \
 && chown learner:learner /home/learner/hr /home/learner/hr/policies.cedar \
 && sha256sum /home/learner/hr/hr.cedarschema /home/learner/hr/entities.json > /usr/local/lib/lab-checks/hr.sha256

USER learner
