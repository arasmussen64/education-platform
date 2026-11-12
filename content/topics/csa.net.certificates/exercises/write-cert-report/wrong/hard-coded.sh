# Wrong: the answers for the first example run, typed in: right there,
# wrong for every other server.
cat > ~/bin/cert-report << 'EOF'
#!/bin/bash
echo "names: shop.test, www.shop.test"
echo "issuer: Report Lab Intermediate"
echo "days-left: 89"
echo "chain: 2"
echo "verify: ok"
EOF
chmod +x ~/bin/cert-report
