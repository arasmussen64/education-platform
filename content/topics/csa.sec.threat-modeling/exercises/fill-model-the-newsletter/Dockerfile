FROM lab-base-tm
# A plain lab on the threat-model base (content/lab-bases/tm): no systemd,
# no network. The base ends as the learner, so the lab's own files go in as
# root and the last line hands back.
USER root

# The design note, and a model of it with eight gaps (___) to fill. What is
# right for this design is in checks.yaml, not in the image.
COPY --chown=learner:learner design.md /home/learner/design.md
COPY --chown=learner:learner --chmod=644 model.tm /home/learner/model.tm

# The same model again, kept where the learner can read it and not change
# it: a check compares the two line by line, so only the gaps may differ,
# and a learner who spoils a line can copy this one back. It holds the
# gaps, not the answers.
RUN mkdir -p /usr/local/lib/lab
COPY --chmod=644 model.tm /usr/local/lib/lab/model.tm

USER learner
