# AlmaLinux 9: a free rebuild of Red Hat Enterprise Linux 9, so dnf, rpm
# and the versionlock plugin are the ones a RHEL or Rocky Linux server has.
# It is a Docker Official Image, kept patched by its project. This is the
# topic's one lab that isn't Ubuntu, so it can't share the other labs'
# first layer.
FROM almalinux:9

# The learner's tools (sudo, nano, less), the versionlock plugin, which
# RHEL's family ships as a package of its own, and the two tools that build
# the lab's packages and repository (rpm-build, createrepo_c); then the
# learner's account with sudo, as a cloud image's default user has.
RUN dnf install -y sudo nano less python3-dnf-plugin-versionlock rpm-build createrepo_c \
 && dnf clean all \
 && useradd -m -s /bin/bash learner \
 && echo 'learner ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/learner \
 && chmod 440 /etc/sudoers.d/learner

# The shop's package repository, and the server's packages and history.
COPY make-repo.sh /usr/local/lib/lab/make-repo.sh
RUN bash /usr/local/lib/lab/make-repo.sh && rm -r /usr/local/lib/lab \
 && mkdir -p /home/learner/patch && chown learner:learner /home/learner/patch

USER learner
WORKDIR /home/learner
CMD ["sleep", "infinity"]
