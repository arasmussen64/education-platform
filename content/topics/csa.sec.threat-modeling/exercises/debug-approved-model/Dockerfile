FROM lab-base-tm
# A plain lab on the threat-model base (content/lab-bases/tm): no systemd,
# no network. The base ends as the learner, so the lab's own files go in as
# root and the last line hands back.
USER root

# The design note, and the model the security board approved last month.
# What is right for this design is in checks.yaml, not in the image.
COPY --chown=learner:learner design.md /home/learner/design.md
COPY --chown=learner:learner --chmod=644 model.tm /home/learner/model.tm

USER learner
