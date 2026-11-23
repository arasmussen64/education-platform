FROM lab-base-policy
# A plain lab on the policy base (content/lab-bases/policy/README.md): the
# base ends as the learner, so the lab's own files go in as root and the
# last line hands back.
USER root

# The shop's schema, people, orders and Alice's session (read-only: the
# system as it is) and the empty policy file, which is the learner's; the
# checks' own case generator, with the checksums of the files that must
# stay as they are, out of the learner's PATH.
COPY shop/ /home/learner/shop/
COPY shop-cases /usr/local/lib/lab-checks/shop-cases
RUN chmod 755 /usr/local/lib/lab-checks/shop-cases \
 && chmod -R a+rX,go-w /home/learner/shop \
 && chown learner:learner /home/learner/shop /home/learner/shop/policies.cedar \
 && sha256sum /home/learner/shop/shop.cedarschema /home/learner/shop/entities.json /home/learner/shop/session-alice.json > /usr/local/lib/lab-checks/shop.sha256

USER learner
