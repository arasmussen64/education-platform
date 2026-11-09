# The lab image for "A report from the shop's logs" (ADR-0018). Built by
# tools/labcheck.py from this folder; nothing here is downloaded at run time.
FROM ubuntu:24.04

# The learner's account, with sudo, and a few comforts: an editor and a pager.
RUN apt-get update \
 && apt-get install -y --no-install-recommends sudo nano less \
 && rm -rf /var/lib/apt/lists/* \
 && useradd -m -s /bin/bash learner \
 && echo 'learner ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/learner \
 && chmod 440 /etc/sudoers.d/learner

# The scenario: the shop's logs, generated deterministically.
COPY seed.sh /usr/local/lib/lab/seed.sh
RUN bash /usr/local/lib/lab/seed.sh && rm -r /usr/local/lib/lab

USER learner
WORKDIR /home/learner
CMD ["sleep", "infinity"]
