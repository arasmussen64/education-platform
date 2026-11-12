# The reference plan, written with cat > FILE << 'EOF', which writes the
# lines up to EOF into FILE (in the lab you'd use nano).
#
# Each subnet holds twice its machines plus the cloud's reserved addresses
# (AWS and Azure keep 5 of every subnet, Google 4), in the smallest block:
#   aws web  2 x 254 + 5 = 513  -> /22 (1024; a /23's 512 is one short)
#   aws app  2 x 120 + 5 = 245  -> /24 (256)
#   aws data 2 x 25  + 5 = 55   -> /26 (64)
#   az web   2 x 500 + 5 = 1005 -> /22 (1024)
#   az app   2 x 60  + 5 = 125  -> /25 (128)
#   az data  2 x 12  + 5 = 29   -> /27 (32)
#   gcp web  2 x 62  + 4 = 128  -> /25 (128, exactly)
#   gcp app  2 x 30  + 4 = 64   -> /26 (64, exactly)
#   gcp data 2 x 6   + 4 = 16   -> /28 (16, exactly)
# Biggest first inside each cloud's summary, so every block starts on a
# multiple of its size. The summaries need at least twice their subnets:
#   aws   3 x (1024 + 256 + 64) = 4032, twice is 8064 -> /19 (8192)
#   azure 1024 + 128 + 32       = 1184, twice is 2368 -> /20 (4096)
#   gcp   128 + 64 + 16         = 208,  twice is 416  -> /23 (512)
# placed one after another from 10.64.0.0, far from 10.72.0.0/16.
mkdir -p ~/plan
cat > ~/plan/plan.txt << 'EOF'
# The company's cloud subnets: NAME BLOCK
aws-a-web   10.64.0.0/22
aws-b-web   10.64.4.0/22
aws-c-web   10.64.8.0/22
aws-a-app   10.64.12.0/24
aws-b-app   10.64.13.0/24
aws-c-app   10.64.14.0/24
aws-a-data  10.64.15.0/26
aws-b-data  10.64.15.64/26
aws-c-data  10.64.15.128/26

az-web      10.64.32.0/22
az-app      10.64.36.0/25
az-data     10.64.36.128/27

gcp-web     10.64.48.0/25
gcp-app     10.64.48.128/26
gcp-data    10.64.48.192/28
EOF
cat > ~/plan/summary.txt << 'EOF'
# Each cloud's block, with room beside its subnets
aws     10.64.0.0/19
azure   10.64.32.0/20
gcp     10.64.48.0/23
EOF
cat ~/plan/plan.txt ~/plan/summary.txt
