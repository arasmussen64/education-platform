# Wrong: vm-a's load of 2.4 on 2 CPUs believed: too few CPUs, from the
# average of vmstat's r, though most of each CPU's time went to the host.
printf 'cause=too-few-cpus\nevidence=2.05\nfix=more-vcpus\n' > ~/diagnosis/vm-a.txt
printf 'cause=cpu-quota\nevidence=55\nfix=raise-cpu-quota\n' > ~/diagnosis/vm-b.txt
printf 'cause=memory-pressure\nevidence=45.12\nfix=more-memory-or-raise-throttle\n' > ~/diagnosis/vm-c.txt
printf 'cause=single-thread\nevidence=99.1\nfix=fix-the-program\n' > ~/diagnosis/vm-d.txt
