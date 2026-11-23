FROM lab-base-pay
# The payments server as the base ships it; nothing is fixed or collected
# in this lab. It adds what the learner reads (the café's systems to scope,
# pay1's controls in scope, the shop's collectors) and the two files with
# gaps to fill, and the checks' own copies and answers.
COPY cafe-systems.txt scope.tsv collectors.tsv /srv/compliance/
COPY scope.starter /home/learner/evidence/scope.txt
COPY pack.starter /home/learner/evidence/pack.tsv
COPY comply.sh pack-check collectors.tsv reference.tsv scope-answers.tsv /usr/local/lib/lab-comp/
RUN cd /usr/local/lib/lab-comp \
 && chmod 755 pack-check \
 && chmod 644 comply.sh collectors.tsv reference.tsv scope-answers.tsv /srv/compliance/* \
 && ln -s /usr/local/lib/lab-pay/oscap-rules /usr/local/bin/oscap-rules \
 && mkdir -p /run/sshd \
 && chown -R learner:learner /home/learner/evidence \
 && sha256sum /srv/compliance/cafe-systems.txt /srv/compliance/scope.tsv /srv/compliance/collectors.tsv > SHA256SUMS
