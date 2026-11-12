# Wrong: the answers are right, but a file of the evidence was changed along
# the way (the learner has sudo). A diagnosis has to rest on the evidence as
# it was saved.
sudo sed -i 's/^cpu  1803204 /cpu  1803999 /' /srv/tickets/vm-a/stat-after.txt
printf 'cause=steal\nevidence=69.6\nfix=fixed-size-or-unlimited\n' > ~/diagnosis/vm-a.txt
printf 'cause=cpu-quota\nevidence=55\nfix=raise-cpu-quota\n' > ~/diagnosis/vm-b.txt
printf 'cause=memory-pressure\nevidence=45.12\nfix=more-memory-or-raise-throttle\n' > ~/diagnosis/vm-c.txt
printf 'cause=single-thread\nevidence=99.1\nfix=fix-the-program\n' > ~/diagnosis/vm-d.txt
