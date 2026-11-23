# The policy labs' shared base (ADR-0018, third amendment). Every
# authentication-and-authorization lab and the strong-authentication topic's
# conditional-access lab start "FROM lab-base-policy" and add only their
# story's files; tools/labcheck.py builds this image first. README.md,
# beside this file, is what an author reads before writing one.
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

# Layer 2: the Cedar command-line tool, the one download from outside
# Ubuntu's archive (Apache-2.0; README.md records the pin). The release's
# archive is checked against its sha256 before anything is unpacked, for
# the machine's own processor: x86_64 (CI, most PCs) or aarch64 (an ARM
# laptop). Its licence files go where Ubuntu keeps every package's.
ARG CEDAR_VERSION=4.14.1
ARG CEDAR_SHA256_X86_64=5833e9f4734eac0d95b3dab7ae119a9212caf0a82e02720b989e2fce6f3bfdad
ARG CEDAR_SHA256_AARCH64=499cfb6a6a7eab28ceca7b24215525a2d107fbf3faca759318a253d485b7d346
RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates xz-utils \
 && rm -rf /var/lib/apt/lists/* \
 && arch="$(uname -m)" \
 && case "$arch" in \
      x86_64) sum="$CEDAR_SHA256_X86_64" ;; \
      aarch64) sum="$CEDAR_SHA256_AARCH64" ;; \
      *) echo "no pinned Cedar build for $arch" >&2; exit 1 ;; \
    esac \
 && name="cedar-policy-cli-$arch-unknown-linux-gnu" \
 && curl -fsSL -o /tmp/cedar.tar.xz "https://github.com/cedar-policy/cedar/releases/download/cedar-policy-cli-v$CEDAR_VERSION/$name.tar.xz" \
 && echo "$sum  /tmp/cedar.tar.xz" | sha256sum -c - \
 && tar -xJf /tmp/cedar.tar.xz -C /tmp \
 && install -m 755 "/tmp/$name/cedar" /usr/local/bin/cedar \
 && install -D -m 644 -t /usr/share/doc/cedar "/tmp/$name/LICENSE" "/tmp/$name/NOTICE" "/tmp/$name/THIRD_PARTY_LICENSES.txt" \
 && rm -rf /tmp/cedar.tar.xz "/tmp/$name" \
 && cedar --version

# Layer 3: the helpers. ask, access-review and ca-whatif are the learner's
# (and the checks'); checklib.py is the checks' library, which makes up its
# requests at check time.
COPY bin/ask bin/access-review bin/ca-whatif /usr/local/bin/
COPY checklib.py /usr/local/lib/policy/
RUN chmod 755 /usr/local/bin/ask /usr/local/bin/access-review /usr/local/bin/ca-whatif /usr/local/lib/policy \
 && chmod 644 /usr/local/lib/policy/checklib.py

# A plain lab: the checker runs "sleep infinity" as the learner. A lab that
# adds files says "USER root" first and "USER learner" last.
USER learner
WORKDIR /home/learner
CMD ["sleep", "infinity"]
