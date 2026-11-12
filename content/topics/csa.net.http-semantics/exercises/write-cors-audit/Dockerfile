FROM ubuntu:24.04
# A plain lab (no systemd, no network of machines): the learner's script is
# the subject. The first RUN is Module 3's plain line, the same in every
# Module 3 plain lab, so Docker builds that layer once (content/README.md,
# "Network labs"). Python is the checks' tool and the stand-in API's, never
# the learner's. ShellCheck, for the check that the script is clean, is a
# second layer, the same as Routing's write lab's.
RUN apt-get update \
 && apt-get install -y --no-install-recommends sudo nano less python3 ipcalc sipcalc openssl curl \
 && rm -rf /var/lib/apt/lists/* \
 && useradd -m -s /bin/bash learner \
 && echo 'learner ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/learner \
 && chmod 440 /etc/sudoers.d/learner
RUN apt-get update \
 && apt-get install -y --no-install-recommends shellcheck \
 && rm -rf /var/lib/apt/lists/*

# The checks' own decision (cors-verdict, the network base's model of a
# browser, copied here because a plain lab has no base), their made-up APIs
# (cors-cases), and the shop's stand-in API that the lab starts on port 8080.
COPY cors-verdict cors-cases cors-compare shop-api start /usr/local/lib/lab/
COPY seed.sh /tmp/seed.sh
RUN chmod 755 /usr/local/lib/lab/cors-verdict /usr/local/lib/lab/cors-cases /usr/local/lib/lab/cors-compare /usr/local/lib/lab/shop-api /usr/local/lib/lab/start \
 && bash /tmp/seed.sh && rm /tmp/seed.sh

USER learner
WORKDIR /home/learner
CMD ["/usr/local/lib/lab/start"]
