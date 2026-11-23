FROM lab-base-id
# Two machines: the staff laptop and the identity provider. The realm file
# carries the strong sign-in flow with four gaps; the people, their keys and
# their app secrets are made here at build, so none is in the repository.
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
# The realm as the learner will mend it (with the four "..." gaps) can't be
# baked, so the image is baked from a plain version with no flow of its own
# (Keycloak's built-in browser flow: a password, and a code only for someone
# who has one). The gappy file is then put back for the learner, and takes
# effect when they apply it.
RUN netlab enable \
 && idlab idp idp https://login.shop.test \
 && idlab names login.shop.test=10.0.5.10 \
 && idlab account alice carol ana ben \
 && idlab seckey alice 0a000000-0000-4000-8000-000000000011 \
 && idlab seckey carol 0a000000-0000-4000-8000-000000000012 \
 && idlab otp ana ben \
 && cp /etc/netns/idp/keycloak/realms/shop.json /tmp/shop.gappy.json \
 && python3 -c "import json; p='/etc/netns/idp/keycloak/realms/shop.json'; d=json.load(open(p)); [d.pop(k, None) for k in ('authenticationFlows', 'authenticatorConfig', 'browserFlow')]; json.dump(d, open(p, 'w'), indent=2)" \
 && idlab bake \
 && cp /tmp/shop.gappy.json /etc/netns/idp/keycloak/realms/shop.json \
 && rm /tmp/shop.gappy.json \
 && netlab seal /etc/netlab/topology
