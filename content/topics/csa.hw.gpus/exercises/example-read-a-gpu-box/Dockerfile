FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive

# A plain lab (no systemd, no GPU): what a GPU server printed is saved as
# files, and the text tools of Module 1 read them. The first RUN is
# identical in every lab of this topic, so Docker builds this layer once.
RUN apt-get update \
 && apt-get install -y --no-install-recommends sudo nano less procps \
 && rm -rf /var/lib/apt/lists/* \
 && useradd -m -s /bin/bash learner \
 && echo 'learner ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/learner \
 && chmod 440 /etc/sudoers.d/learner

COPY seed.sh /usr/local/lib/lab/seed.sh
RUN bash /usr/local/lib/lab/seed.sh && rm /usr/local/lib/lab/seed.sh

USER learner
WORKDIR /home/learner
CMD ["sleep", "infinity"]
