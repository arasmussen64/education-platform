# The threat-model labs' shared base (ADR-0018, third amendment). Every
# threat-modeling lab and Checkpoint 4 part 1 start "FROM lab-base-tm" and
# add only their design notes and the learner's model; tools/labcheck.py
# builds this image first. README.md, beside this file, is what an author
# reads before writing one.
FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive

# Layer 1: byte-identical to the first RUN of Module 3's plain labs
# (content/README.md, "Network labs"), so Docker reuses that layer from its
# cache. Change it only with all of them. Python is the checks' tool, never
# the learner's.
RUN apt-get update \
 && apt-get install -y --no-install-recommends sudo nano less python3 ipcalc sipcalc openssl curl \
 && rm -rf /var/lib/apt/lists/* \
 && useradd -m -s /bin/bash learner \
 && echo 'learner ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/learner \
 && chmod 440 /etc/sudoers.d/learner

# Layer 2: tm-check, the checker for threat models written as plain lines of
# text. It holds the format and the general rules only; what is right for
# one design (the reference) stays in that lab's checks.yaml, outside the
# image the learner can read.
COPY --chmod=755 tm-check /usr/local/bin/tm-check

# A plain lab: the checker runs "sleep infinity" as the learner. A lab that
# adds files says "USER root" first and "USER learner" last.
USER learner
WORKDIR /home/learner
CMD ["sleep", "infinity"]
