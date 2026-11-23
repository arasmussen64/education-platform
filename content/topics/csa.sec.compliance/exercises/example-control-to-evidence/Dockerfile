FROM lab-base-pay
# The payments server as the base ships it: root may log in over SSH with a
# key, and nothing has been measured yet. The lab adds a description of
# five of the shop's systems to scope, short names for two of the base's
# helpers (oscap-rules, root-login), and the checks' own files.
COPY systems.txt /srv/compliance/systems.txt
COPY comply.sh pack-check reference.tsv scope-answers.tsv /usr/local/lib/lab-comp/
RUN cd /usr/local/lib/lab-comp \
 && chmod 755 pack-check \
 && chmod 644 comply.sh reference.tsv scope-answers.tsv /srv/compliance/systems.txt \
 && ln -s /usr/local/lib/lab-pay/oscap-rules /usr/local/bin/oscap-rules \
 && ln -s /usr/local/lib/lab-pay/root-login /usr/local/bin/root-login \
 && mkdir -p /run/sshd \
 && sha256sum /srv/compliance/systems.txt > SHA256SUMS
