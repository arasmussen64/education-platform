FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive

# A plain lab (no systemd): programs and their architectures are the
# subject. The C compiler for this machine (x86-64) and a cross-compiler for
# 64-bit Arm with its C library; QEMU's user-mode emulators, which run one
# program built for another CPU (every one but the Arm and x86-64 emulators
# is deleted, to keep the image smaller); file, binutils (objdump, readelf),
# zip and unzip; and the learner's account with sudo. Identical in every lab
# of this topic, so Docker builds this layer once for all of them.
RUN apt-get update \
 && apt-get install -y --no-install-recommends gcc libc6-dev gcc-aarch64-linux-gnu libc6-dev-arm64-cross qemu-user-static file binutils unzip zip sudo nano less procps \
 && rm -rf /var/lib/apt/lists/* \
 && find /usr/bin -name 'qemu-*-static' ! -name qemu-aarch64-static ! -name qemu-x86_64-static -delete \
 && useradd -m -s /bin/bash learner \
 && echo 'learner ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/learner \
 && chmod 440 /etc/sudoers.d/learner

COPY seed.sh what-arch.starter /usr/local/lib/lab/
RUN bash /usr/local/lib/lab/seed.sh && rm -r /usr/local/lib/lab

USER learner
WORKDIR /home/learner
CMD ["sleep", "infinity"]
