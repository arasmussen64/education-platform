FROM lab-base-tm
# A plain lab on the threat-model base (content/lab-bases/tm): no systemd,
# no network. The base ends as the learner, so the lab's own files go in as
# root and the last line hands back.
USER root

# The design note to read, and the empty model the learner writes. What is
# right for this design is in checks.yaml, not in the image.
COPY --chown=learner:learner design.md /home/learner/design.md
RUN install -o learner -g learner -m 644 /dev/null /home/learner/model.tm

USER learner
