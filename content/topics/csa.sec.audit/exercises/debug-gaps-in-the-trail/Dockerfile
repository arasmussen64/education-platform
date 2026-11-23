FROM lab-base-pay
# The payments server a year after its audit trail was set up. The image
# holds the trail's policy and its journal's settings as they were built;
# the sealing keys, some weeks of history and last week's changes are made
# at the first boot by lab-story.service (story.sh says why), from the
# files in /usr/local/lib/lab/story, which it removes when it is done.
COPY trail.sh policy-check story.sh /usr/local/lib/lab/
COPY 40-quiet.conf 60-disk.conf /usr/local/lib/lab/story/
COPY audit.conf /etc/shop/audit.conf
COPY journald@audit.conf /etc/systemd/journald@audit.conf
COPY lab-story.service /etc/systemd/system/lab-story.service
RUN chmod 644 /usr/local/lib/lab/trail.sh /etc/shop/audit.conf /etc/systemd/journald@audit.conf /etc/systemd/system/lab-story.service \
 && chmod 755 /usr/local/lib/lab/policy-check /usr/local/lib/lab/story.sh \
 && mkdir -p /srv/auditors \
 && systemctl enable lab-story.service
