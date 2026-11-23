FROM lab-base-policy
# A plain lab on the policy base: the base ends as the learner, so the lab's
# own files go in as root and the last line hands back.
USER root

# The shop's schema, people and orders (read-only: the system as it is) and
# the empty policy file, which is the learner's; scenery for the base's
# helpers (a service's access log, four conditional-access policies),
# read-only; and the checks' own case generator with the checksums of the
# files that must stay as they are, out of the learner's PATH.
COPY shop/ /home/learner/shop/
COPY scenery/ /srv/probe/
COPY --chmod=755 shop-cases /usr/local/lib/lab-checks/shop-cases
RUN chmod -R a+rX,go-w /srv/probe /home/learner/shop \
 && chown learner:learner /home/learner/shop /home/learner/shop/policies.cedar \
 && sha256sum /home/learner/shop/shop.cedarschema /home/learner/shop/entities.json > /usr/local/lib/lab-checks/shop.sha256

USER learner
