# The checkout's threat model, in the order of work. Write each part's
# lines under its heading, one fact a line; a line can only use names the
# lines above it define.
#
# 1. The zones: one owner, one network, nothing filtering inside.
#
# 2. The elements (external, process or store), each in its zone.
#
# 3. The flows, from the side that starts each.
#
# 4. A scope line for every process and store the shop runs.
#
# 5. The threats on every flow that crosses a boundary, and on any flow the
#    design describes as weak, rated by the design's scales; none lines for
#    every other letter of a crossing flow.
#
# 6. A control for every risk of 6 or more, a control or an accept for
#    the rest; the top line.
#
# 7. The two ATT&CK techniques, and the attack tree with its cheapest path.
