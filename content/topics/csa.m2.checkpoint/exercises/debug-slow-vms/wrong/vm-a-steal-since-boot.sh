# Wrong: vm-a's steal read from stat-after.txt alone, the share since boot
# (4.2%), not the minute's growth.
printf 'cause=steal\nevidence=4.2\nfix=fixed-size-or-unlimited\n' > ~/diagnosis/vm-a.txt
printf 'cause=cpu-quota\nevidence=55\nfix=raise-cpu-quota\n' > ~/diagnosis/vm-b.txt
printf 'cause=memory-pressure\nevidence=45.12\nfix=more-memory-or-raise-throttle\n' > ~/diagnosis/vm-c.txt
printf 'cause=single-thread\nevidence=99.1\nfix=fix-the-program\n' > ~/diagnosis/vm-d.txt
