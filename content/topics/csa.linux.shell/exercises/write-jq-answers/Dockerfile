# The lab image for "Four questions about a JSON log" (ADR-0018). Built by
# tools/labcheck.py from this folder.
FROM ubuntu:24.04

RUN apt-get update \
 && apt-get install -y --no-install-recommends sudo nano less \
 && rm -rf /var/lib/apt/lists/* \
 && useradd -m -s /bin/bash learner \
 && echo 'learner ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/learner \
 && chmod 440 /etc/sudoers.d/learner

# jq, the tool that reads JSON. Only this lab needs it, so it has a RUN line
# of its own and the line above stays the one the topic's other labs share.
RUN apt-get update \
 && apt-get install -y --no-install-recommends jq \
 && rm -rf /var/lib/apt/lists/*

# The shop's usual logs (the same seed as the topic's other labs), and the
# API's log of JSON lines, which only this lab has.
COPY seed.sh seed-json.sh /usr/local/lib/lab/
RUN bash /usr/local/lib/lab/seed.sh && bash /usr/local/lib/lab/seed-json.sh && rm -r /usr/local/lib/lab

USER learner
WORKDIR /home/learner
CMD ["sleep", "infinity"]
