FROM lab-base-pay
# The payments server with a policy that records sign-ins, refunds and card
# updates (the base's own records sign-ins only), an audit journal that
# isn't sealed yet, and a folder for what the walkthrough saves.
COPY trail.sh /usr/local/lib/lab/trail.sh
COPY audit.conf /etc/shop/audit.conf
RUN chmod 644 /usr/local/lib/lab/trail.sh /etc/shop/audit.conf \
 && mkdir -p /home/learner/example \
 && chown learner:learner /home/learner/example
