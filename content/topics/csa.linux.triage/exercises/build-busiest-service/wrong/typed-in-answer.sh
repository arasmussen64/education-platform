# Wrong: the answer for this machine, worked out once and typed into the
# script. It measures nothing, so it can't see a service that wasn't there
# when it was written.
cat > ~/bin/busiest-service <<'EOF'
#!/bin/bash
echo "CPU used in the last second (ms), busiest first:"
echo "  shop-worker: 998 ms"
echo "  shop-api: 0 ms"
echo "  shop-db: 0 ms"
echo "busiest: shop-worker"
EOF
chmod +x ~/bin/busiest-service
