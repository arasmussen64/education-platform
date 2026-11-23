FROM lab-base-tm
# A plain lab on the threat-model base (content/lab-bases/tm): no systemd,
# no network. The learner's script is the subject. The base ends as the
# learner, so the lab's own files go in as root and the last line hands
# back.
USER root

# The checks' own side (review-cases makes models up as a check runs and
# says what the script must print for each), a copy of the example the
# checks read, and the example the learner tries the script on.
RUN mkdir -p /usr/local/lib/lab
COPY --chmod=755 review-cases /usr/local/lib/lab/review-cases
COPY --chmod=644 example.tm /usr/local/lib/lab/example.tm
COPY --chown=learner:learner --chmod=644 example.tm /home/learner/example.tm

USER learner
