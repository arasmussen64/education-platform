FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive

# A plain lab (no systemd): bash is the subject. ShellCheck for the labs
# that lint a script, and the learner's account with sudo. The first RUN is
# identical in every scripting lab, so Docker builds this layer once.
RUN apt-get update \
 && apt-get install -y --no-install-recommends sudo nano less shellcheck ca-certificates \
 && rm -rf /var/lib/apt/lists/* \
 && useradd -m -s /bin/bash learner \
 && echo 'learner ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/learner \
 && chmod 440 /etc/sudoers.d/learner

COPY seed.sh /usr/local/lib/lab/seed.sh
RUN bash /usr/local/lib/lab/seed.sh && rm -r /usr/local/lib/lab

USER learner
WORKDIR /home/learner
CMD ["sleep", "infinity"]
