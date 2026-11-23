FROM lab-base-pay
# pay2, the shop's second payments server, on the morning after a patch run
# that printed no error. Three things were set up on it months ago, each for
# a reason that sounded sensible at the time, and each is why the run left
# something behind:
#  - a copy of the SSH server program kept beside the package's, which the
#    SSH unit runs instead of the package's (a drop-in);
#  - a hold on one package;
#  - a pin that ties another to the version it had.
# Then Monday's patch run itself, run here as the server ran it, with its
# output kept in /var/log/patch-run.log; and, for the checks, what SSH's
# settings and host keys are.
COPY 50-keep.conf /etc/systemd/system/ssh.service.d/50-keep.conf
COPY deploy-tools /etc/apt/preferences.d/deploy-tools
RUN chmod 644 /etc/systemd/system/ssh.service.d/50-keep.conf /etc/apt/preferences.d/deploy-tools \
 && mkdir -p /usr/local/lib/lab-vuln /run/sshd \
 && cp -p /usr/sbin/sshd /usr/local/sbin/sshd-stable \
 && apt-mark hold rsync > /dev/null \
 && apt-get update > /dev/null \
 && (echo '$ apt-get update && apt-get -y upgrade'; apt-get -y upgrade 2>&1) > /var/log/patch-run.log \
 && cd /usr/local/lib/lab-vuln \
 && sshd -T > sshd-T \
 && for key in /etc/ssh/ssh_host_*_key.pub; do ssh-keygen -lf "$key"; done > host-keys
