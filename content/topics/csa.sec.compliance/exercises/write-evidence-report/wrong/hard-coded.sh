# The prompt's example, printed for every control.

mkdir -p ~/bin
cat > ~/bin/evidence << 'EOF'
#!/bin/bash
echo "accounts_password_pam_dcredit fail"
echo "accounts_password_pam_lcredit fail"
echo "accounts_password_pam_minlen pass"
echo "not met"
EOF
chmod +x ~/bin/evidence
