# Wrong: instead of BBR, the link's loss is taken away live with tc, so
# CUBIC runs fast. The link isn't the shop's to change, and shop still
# uses CUBIC.
on wan tc qdisc change dev eth1 root netem rate 50mbit delay 25ms loss 0% limit 2000
