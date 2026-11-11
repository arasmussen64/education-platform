# The lab image for "Finish licence-count" (ADR-0018). Built by
# tools/labcheck.py from this folder; nothing here is downloaded at run time.
FROM ubuntu:24.04

# The learner's account, with sudo, and an editor and a pager. This first RUN
# is the same as Shell essentials' labs and every lab of this topic, so Docker
# builds the layer once for all of them.
RUN apt-get update \
 && apt-get install -y --no-install-recommends sudo nano less \
 && rm -rf /var/lib/apt/lists/* \
 && useradd -m -s /bin/bash learner \
 && echo 'learner ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/learner \
 && chmod 440 /etc/sudoers.d/learner

# The workbench under /srv/licensing, and the script with its gaps in
# ~/bin/licence-count.
COPY licence-count.starter /usr/local/lib/lab/licence-count.starter
COPY seed.sh /usr/local/lib/lab/seed.sh
RUN bash /usr/local/lib/lab/seed.sh && rm -r /usr/local/lib/lab

USER learner
WORKDIR /home/learner
CMD ["sleep", "infinity"]
