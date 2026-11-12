# Wrong: vm-c's disk waits believed: a slow disk, with writes a second as
# the evidence, though the waits are the swapping and io.max sets no cap.
printf 'cause=steal\nevidence=69.6\nfix=fixed-size-or-unlimited\n' > ~/diagnosis/vm-a.txt
printf 'cause=cpu-quota\nevidence=55\nfix=raise-cpu-quota\n' > ~/diagnosis/vm-b.txt
printf 'cause=disk-cap\nevidence=38.5\nfix=faster-disk-tier\n' > ~/diagnosis/vm-c.txt
printf 'cause=single-thread\nevidence=99.1\nfix=fix-the-program\n' > ~/diagnosis/vm-d.txt
