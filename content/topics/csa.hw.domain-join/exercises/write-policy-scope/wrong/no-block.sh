# Wrong: Contractors never blocks inheritance, so frank also gets Lock
# screen from Staff and the Default Domain Policy from the domain.
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
# ...except the baseline, linked to the whole domain and enforced, which a
# block can't stop.
baseline=$(on-dc samba-tool gpo create 'Security baseline' -U Administrator --password='Shop-Admin-1' | grep -o '{.*}')
on-dc samba-tool gpo setlink 'DC=ad,DC=shop,DC=test' "$baseline" --enforce -U Administrator --password='Shop-Admin-1'
