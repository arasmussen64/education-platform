# Wrong: vm-c's evidence read from the wrong field of pressure/memory:
# avg60, the minute's average, where the README asks for avg10.
printf 'cause=steal\nevidence=69.6\nfix=fixed-size-or-unlimited\n' > ~/diagnosis/vm-a.txt
printf 'cause=cpu-quota\nevidence=55\nfix=raise-cpu-quota\n' > ~/diagnosis/vm-b.txt
printf 'cause=memory-pressure\nevidence=43.80\nfix=more-memory-or-raise-throttle\n' > ~/diagnosis/vm-c.txt
printf 'cause=single-thread\nevidence=99.1\nfix=fix-the-program\n' > ~/diagnosis/vm-d.txt
