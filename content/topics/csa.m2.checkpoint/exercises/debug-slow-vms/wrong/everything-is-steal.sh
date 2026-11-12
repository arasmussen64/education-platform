# Wrong: every slow VM put down to steal, the cause this module made famous,
# with each VM's steal over the minute as its evidence.
printf 'cause=steal\nevidence=69.6\nfix=fixed-size-or-unlimited\n' > ~/diagnosis/vm-a.txt
printf 'cause=steal\nevidence=0\nfix=fixed-size-or-unlimited\n' > ~/diagnosis/vm-b.txt
printf 'cause=steal\nevidence=0\nfix=fixed-size-or-unlimited\n' > ~/diagnosis/vm-c.txt
printf 'cause=steal\nevidence=0.1\nfix=fixed-size-or-unlimited\n' > ~/diagnosis/vm-d.txt
