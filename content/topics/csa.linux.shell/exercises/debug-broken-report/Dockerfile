# The lab image for "The report that lies" (ADR-0018). Built by
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

# The buggy script, owned by the learner so they can fix it.
COPY report.starter /home/learner/bin/report
RUN chmod 755 /home/learner/bin/report && chown -R learner:learner /home/learner/bin

USER learner
WORKDIR /home/learner
CMD ["sleep", "infinity"]
