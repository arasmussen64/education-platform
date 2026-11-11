# The lab image for "Price one estate" (ADR-0018). Built by tools/labcheck.py
# from this folder; nothing here is downloaded at run time.
FROM ubuntu:24.04

# The learner's account, with sudo, and an editor and a pager. This first RUN
# is the same as Shell essentials' labs and every lab of this topic, so Docker
# builds the layer once for all of them. awk (mawk), tail, grep and
# sha256sum come with the base image.
RUN apt-get update \
 && apt-get install -y --no-install-recommends sudo nano less \
 && rm -rf /var/lib/apt/lists/* \
 && useradd -m -s /bin/bash learner \
 && echo 'learner ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/learner \
 && chmod 440 /etc/sudoers.d/learner

# The workbench: a README and the shop's estate, under /srv/licensing.
COPY seed.sh /usr/local/lib/lab/seed.sh
RUN bash /usr/local/lib/lab/seed.sh && rm /usr/local/lib/lab/seed.sh

USER learner
WORKDIR /home/learner
CMD ["sleep", "infinity"]
