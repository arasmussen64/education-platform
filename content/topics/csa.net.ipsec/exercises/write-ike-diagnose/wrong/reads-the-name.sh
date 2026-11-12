# Wrong: the script answers from the log file's name, not from what the log
# says, as if each log were named after what went wrong in it. It reads
# nothing inside the file.
cat > ~/bin/ike-diagnose << 'EOF'
#!/bin/bash
log=$1
if [[ ! -r $log ]]; then
  echo "ike-diagnose: can't read ${log:-a log}" >&2
  exit 1
fi
case $(basename "$log") in
  *rekey*) echo 'phase 2: rekey failed' ;;
  *ike-proposal*) echo 'phase 1: no proposal chosen' ;;
  *auth*) echo 'phase 1: authentication failed' ;;
  *esp-proposal*) echo 'phase 2: no proposal chosen' ;;
  *selectors*) echo 'phase 2: traffic selectors unacceptable' ;;
  *no-answer*) echo 'no answer from the peer' ;;
  *) echo 'up' ;;
esac
EOF
chmod +x ~/bin/ike-diagnose
