# Wrong: vm-a's cause found, and a dedicated host chosen for it: ten times
# the price, and a host of its own does nothing for a burstable VM's spent
# credits.
printf 'cause=steal\nevidence=69.6\nfix=dedicated-host\n' > ~/diagnosis/vm-a.txt
printf 'cause=cpu-quota\nevidence=55\nfix=raise-cpu-quota\n' > ~/diagnosis/vm-b.txt
printf 'cause=memory-pressure\nevidence=45.12\nfix=more-memory-or-raise-throttle\n' > ~/diagnosis/vm-c.txt
printf 'cause=single-thread\nevidence=99.1\nfix=fix-the-program\n' > ~/diagnosis/vm-d.txt
