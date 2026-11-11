# Wrong: Contractors is made at the top of the domain, beside Staff, instead
# of inside it. Every list of GPOs comes out right, because Contractors
# blocks what's above it anyway; but the layout isn't the one asked for, and
# the next GPO linked to Staff for all staff misses the contractors.
on-dc samba-tool ou create 'OU=Staff'
on-dc samba-tool ou create 'OU=Engineering,OU=Staff'
on-dc samba-tool ou create 'OU=Contractors'

on-dc samba-tool user move alice 'OU=Engineering,OU=Staff'
on-dc samba-tool user move bob 'OU=Staff'
on-dc samba-tool user move frank 'OU=Contractors'

lock=$(on-dc samba-tool gpo create 'Lock screen' -U Administrator --password='Shop-Admin-1' | grep -o '{.*}')
on-dc samba-tool gpo setlink 'OU=Staff,DC=ad,DC=shop,DC=test' "$lock" -U Administrator --password='Shop-Admin-1'
tools=$(on-dc samba-tool gpo create 'Engineering tools' -U Administrator --password='Shop-Admin-1' | grep -o '{.*}')
on-dc samba-tool gpo setlink 'OU=Engineering,OU=Staff,DC=ad,DC=shop,DC=test' "$tools" -U Administrator --password='Shop-Admin-1'
limits=$(on-dc samba-tool gpo create 'Contractor limits' -U Administrator --password='Shop-Admin-1' | grep -o '{.*}')
on-dc samba-tool gpo setlink 'OU=Contractors,DC=ad,DC=shop,DC=test' "$limits" -U Administrator --password='Shop-Admin-1'
on-dc samba-tool gpo setinheritance 'OU=Contractors,DC=ad,DC=shop,DC=test' block -U Administrator --password='Shop-Admin-1'
baseline=$(on-dc samba-tool gpo create 'Security baseline' -U Administrator --password='Shop-Admin-1' | grep -o '{.*}')
on-dc samba-tool gpo setlink 'DC=ad,DC=shop,DC=test' "$baseline" --enforce -U Administrator --password='Shop-Admin-1'
