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

# The small VM every hypervisors lab boots, /opt/vm, built the same way in
# each lab, so Docker builds this layer once too.
COPY vm/ /usr/local/lib/lab/vm/
RUN bash /usr/local/lib/lab/vm/build-guest.sh

# The shop's VM: its launcher, its settings, its disk.
COPY shop-vm shop-vm.conf README seed.sh /usr/local/lib/lab/
RUN bash /usr/local/lib/lab/seed.sh && rm -r /usr/local/lib/lab

USER learner
WORKDIR /home/learner
CMD ["sleep", "infinity"]
