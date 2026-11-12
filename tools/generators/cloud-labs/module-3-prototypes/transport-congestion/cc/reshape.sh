#!/bin/bash
RATE=$1; DELAY=$2; LOSS=$3; LIMIT=${4:-1000}
ip netns exec wan tc qdisc change dev b0 root netem rate $RATE delay $DELAY loss $LOSS limit $LIMIT
ip netns exec wan tc qdisc change dev a0 root netem delay $DELAY limit $LIMIT
