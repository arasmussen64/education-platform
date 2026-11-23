FROM lab-base-id
# The network, each machine's own files, the two pages the web team wrote
# and the nightly job.
COPY topology /etc/netlab/topology
COPY machines/ /etc/netns/
COPY shop/ /usr/local/lib/shop/
COPY bin/ /usr/local/bin/
COPY base-fix make-jwk resign-token /usr/local/lib/shop/
# Everything secret or signed is made here, at build, so none of it is in
# the repository: the lab's CA and the two servers' certificates, a secret
# for each of the two clients the learner will register, the supplier
# portal's, two people's passwords and the realm's two signing keys. The
# partners realm is given the same two keys (the lab's story: both realms
# were set up from one template, keys and all).
#
# The Apache modules are switched on and each site is its unfinished file.
# /etc/reorder exists on the jobs server, empty, for the job's own file.
# resign-token is the checks' own tool (root only): it signs a token with
# the realm's own key, to show the API tokens no real client could ask for.
RUN chmod 755 /usr/local/lib/shop/site/* /usr/local/lib/shop/api/* /usr/local/bin/reorder \
 && chmod 700 /usr/local/lib/shop/resign-token \
 && python3 /usr/local/lib/shop/base-fix \
 && netlab enable \
 && idlab idp idp https://login.shop.test \
 && idlab names login.shop.test=10.0.5.10 stock.shop.test=10.0.5.22 api.shop.test=10.0.5.30 \
 && idlab cert stock stock.shop.test \
 && idlab cert api api.shop.test \
 && idlab secret STOCK_WEB_SECRET REORDER_JOB_SECRET SUPPLIER_PORTAL_SECRET \
 && idlab account ana ben \
 && idlab key shop 2025 passive \
 && idlab key shop 2026 \
 && cp -a /etc/netns/idp/keycloak/keys/shop /etc/netns/idp/keycloak/keys/partners \
 && idlab a2 stock mod auth_openidc \
 && idlab a2 stock site stock \
 && idlab a2 api mod oauth2 \
 && idlab a2 api site api \
 && mkdir -p /etc/reorder /etc/netns/jobs/reorder \
 && idlab bake \
 && netlab seal /etc/netlab/topology /etc/netns/idp/keycloak/realms/partners.json \
      /usr/local/lib/shop/site/me /usr/local/lib/shop/api/reorder /usr/local/bin/reorder
