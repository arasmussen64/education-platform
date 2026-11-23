FROM lab-base-pay
# The payments server part-way through its hardening, so that some rules
# of the benchmark pass and some fail: root's login over SSH is switched
# off and the minimum password length is set, and nothing else is. The lab
# adds a short name for the base's oscap-rules helper and the checks' own
# program, which makes up crosswalks as it runs (only root may read or run
# it: a script lab's answers aren't a tool the learner's script can call).
COPY evidence-cases /usr/local/lib/lab-comp/evidence-cases
RUN chmod 700 /usr/local/lib/lab-comp /usr/local/lib/lab-comp/evidence-cases \
 && ln -s /usr/local/lib/lab-pay/oscap-rules /usr/local/bin/oscap-rules \
 && mkdir -p /run/sshd \
 && echo 'PermitRootLogin no' > /etc/ssh/sshd_config.d/60-hardening.conf \
 && echo 'minlen = 14' >> /etc/security/pwquality.conf \
 && install -d -o learner -g learner /home/learner/bin
