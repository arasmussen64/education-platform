# Wrong: the four GPOs are created and never linked, so none of them
# reaches anyone: a GPO does nothing until it is linked.
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
tools=$(on-dc samba-tool gpo create 'Engineering tools' -U Administrator --password='Shop-Admin-1' | grep -o '{.*}')
limits=$(on-dc samba-tool gpo create 'Contractor limits' -U Administrator --password='Shop-Admin-1' | grep -o '{.*}')

# Contractors takes nothing from above: block inheritance on the folder...
# ...except the baseline, linked to the whole domain and enforced, which a
# block can't stop.
baseline=$(on-dc samba-tool gpo create 'Security baseline' -U Administrator --password='Shop-Admin-1' | grep -o '{.*}')
