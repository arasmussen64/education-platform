# A reference, one way among several: the folders and the people first,
# then each GPO, created and linked. A GPO is linked by its GUID, which
# `gpo create` prints, so each one is saved in a variable as it's made:
# `$(...)` runs a command and hands back what it printed, and grep -o keeps
# only the part in braces. The password is on the command line only so this
# file can run by itself; leave --password off and samba-tool asks for it.

# 1. The folders: Staff at the top, Engineering and Contractors inside it.
on-dc samba-tool ou create 'OU=Staff'
on-dc samba-tool ou create 'OU=Engineering,OU=Staff'
on-dc samba-tool ou create 'OU=Contractors,OU=Staff'

# 2. The people. carol stays in CN=Users.
on-dc samba-tool user move alice 'OU=Engineering,OU=Staff'
on-dc samba-tool user move bob 'OU=Staff'
on-dc samba-tool user move frank 'OU=Contractors,OU=Staff'

# 3. The policies, each created and linked once.
lock=$(on-dc samba-tool gpo create 'Lock screen' -U Administrator --password='Shop-Admin-1' | grep -o '{.*}')
on-dc samba-tool gpo setlink 'OU=Staff,DC=ad,DC=shop,DC=test' "$lock" -U Administrator --password='Shop-Admin-1'
tools=$(on-dc samba-tool gpo create 'Engineering tools' -U Administrator --password='Shop-Admin-1' | grep -o '{.*}')
on-dc samba-tool gpo setlink 'OU=Engineering,OU=Staff,DC=ad,DC=shop,DC=test' "$tools" -U Administrator --password='Shop-Admin-1'
limits=$(on-dc samba-tool gpo create 'Contractor limits' -U Administrator --password='Shop-Admin-1' | grep -o '{.*}')
on-dc samba-tool gpo setlink 'OU=Contractors,OU=Staff,DC=ad,DC=shop,DC=test' "$limits" -U Administrator --password='Shop-Admin-1'

# Contractors takes nothing from above: block inheritance on the folder...
on-dc samba-tool gpo setinheritance 'OU=Contractors,OU=Staff,DC=ad,DC=shop,DC=test' block -U Administrator --password='Shop-Admin-1'
# ...except the baseline, linked to the whole domain and enforced, which a
# block can't stop.
baseline=$(on-dc samba-tool gpo create 'Security baseline' -U Administrator --password='Shop-Admin-1' | grep -o '{.*}')
on-dc samba-tool gpo setlink 'DC=ad,DC=shop,DC=test' "$baseline" --enforce -U Administrator --password='Shop-Admin-1'

# 4. Who gets what.
for person in alice bob carol frank; do
  on-dc samba-tool gpo list "$person"
done
