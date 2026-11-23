FROM lab-base-policy
# A plain lab on the policy base: the base ends as the learner, so the lab's
# own files go in as root and the last line hands back.
USER root

# The directory (who there is: people, groups, roles and apps) and the named
# locations are the world as it is, read-only with a checksum. The learner
# writes one JSON policy a file in ~/ca/policies, which starts empty. The
# checks' case generator makes up its own people and sign-ins at check time.
COPY ca/ /home/learner/ca/
COPY --chmod=755 ca-cases /usr/local/lib/lab-checks/ca-cases
RUN install -d -o learner -g learner /home/learner/ca/policies \
 && chmod -R a+rX,go-w /home/learner/ca \
 && chown -R learner:learner /home/learner/ca \
 && sha256sum /home/learner/ca/directory.json /home/learner/ca/locations.json > /usr/local/lib/lab-checks/scenery.sha256

USER learner
