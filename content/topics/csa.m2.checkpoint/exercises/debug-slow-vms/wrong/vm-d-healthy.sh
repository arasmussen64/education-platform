# Wrong: vm-d's average believed: a quarter busy looks healthy, though one
# of its four CPUs is flat out the whole minute.
printf 'cause=steal\nevidence=69.6\nfix=fixed-size-or-unlimited\n' > ~/diagnosis/vm-a.txt
printf 'cause=cpu-quota\nevidence=55\nfix=raise-cpu-quota\n' > ~/diagnosis/vm-b.txt
printf 'cause=memory-pressure\nevidence=45.12\nfix=more-memory-or-raise-throttle\n' > ~/diagnosis/vm-c.txt
printf 'cause=healthy\nevidence=0\nfix=nothing\n' > ~/diagnosis/vm-d.txt
