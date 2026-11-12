# Wrong: conntrack's table flushed, "to clear out the stuck connections",
# and nothing else: the rules that cause all three faults are untouched.
on gw conntrack -F
