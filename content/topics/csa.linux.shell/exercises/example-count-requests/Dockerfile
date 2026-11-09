# The lab image for "Two questions about a log" (ADR-0018). Built by
# tools/labcheck.py from this folder.
FROM ubuntu:24.04

RUN apt-get update \
 && apt-get install -y --no-install-recommends sudo nano less \
 && rm -rf /var/lib/apt/lists/* \
 && useradd -m -s /bin/bash learner \
 && echo 'learner ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/learner \
 && chmod 440 /etc/sudoers.d/learner

COPY seed.sh /usr/local/lib/lab/seed.sh
RUN bash /usr/local/lib/lab/seed.sh && rm -r /usr/local/lib/lab

USER learner
WORKDIR /home/learner
CMD ["sleep", "infinity"]
