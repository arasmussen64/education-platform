# "Auditors change nothing" written as a forbid on everything an auditor
# does: they can't read the log, or see their own salary.
cd ~/hr
sed -i '/@id("managers-see-their-department")/{n;s/permit (principal, /permit (principal in Role::"manager", /}' policies.cedar
sed -i 's/^unless { resource.requested_by == principal };/when { resource.requested_by == principal };/' policies.cedar
cat >> policies.cedar <<'EOF'

forbid (principal in Role::"auditor", action, resource);
EOF
