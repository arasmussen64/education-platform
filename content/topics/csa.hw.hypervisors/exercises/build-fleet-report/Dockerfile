FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive

# A plain lab (no systemd running): QEMU and a stock Ubuntu kernel, to boot a
# small virtual machine without hardware help; busybox, cpio and zstd to
# build the guest's tiny root filesystem from; systemd for its
# systemd-detect-virt program only; lscpu, lspci and lsmod to read the
# machine; the learner's account with sudo. The first RUN is identical in
# every hypervisors lab, so Docker builds this layer once.
RUN apt-get update \
 && apt-get install -y --no-install-recommends qemu-system-x86 qemu-utils linux-image-virtual busybox-static cpio zstd systemd util-linux pciutils kmod sudo nano less procps file \
 && rm -rf /var/lib/apt/lists/* \
 && useradd -m -s /bin/bash learner \
 && echo 'learner ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/learner \
 && chmod 440 /etc/sudoers.d/learner

# The shop's fleet, a folder per server, and a second fleet laid out the
# same way for the checks. Each folder's SOURCE.txt says whether it was
# captured from a real machine or built from documentation.
COPY fleet-a/ /srv/fleet-a/
COPY fleet-b/ /usr/local/share/lab/fleet-b/
COPY seed.sh /usr/local/lib/lab/seed.sh
RUN bash /usr/local/lib/lab/seed.sh && rm -r /usr/local/lib/lab

USER learner
WORKDIR /home/learner
CMD ["sleep", "infinity"]
