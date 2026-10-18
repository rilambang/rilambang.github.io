#!/bin/sh
# Prose guard. Run before any push that touches written content.
#
# The term list is deliberately NOT in this repo: committing it would publish the exact
# strings it exists to suppress. One term per line, in prose-denylist.local at the repo
# root — already ignored by the `*.local` rule in .gitignore. Blank lines and lines
# starting with `#` are comments and are not treated as patterns. No file, no terms, and
# only the structural checks below run.
#
# Runs against docs/ as well as public/, on purpose: the phone number that got through in
# this project was caught in the build output, not in the source. Grep the served
# artifact, never the input.
set -e
cd "$(dirname "$0")/.."

targets=""
for d in public/blog docs/blog; do
  [ -d "$d" ] && targets="$targets $d"
done
if [ -z "$targets" ]; then
  echo "✗ no blog directory found — run: npm run build"
  exit 1
fi

status=0

# Real terms only: strip comments and blanks, or a bare '#' becomes a pattern that
# matches every hex colour and HTML entity in the tree.
terms=$(sed -e 's/#.*$//' -e '/^[[:space:]]*$/d' prose-denylist.local 2>/dev/null || true)
if [ -n "$terms" ]; then
  if echo "$terms" | grep -rniEf - $targets; then
    echo "✗ prose-denylist.local match above — generalize the noun, keep the mechanics"
    status=1
  fi
else
  echo "· no denylist terms — term check skipped"
fi

# Structural: PII that must never appear in prose, whatever the denylist says.
if grep -rnE '(\+62|\(0[0-9]{2}\)|08[0-9]{2})[ 0-9-]{5,}' $targets; then
  echo "✗ phone-shaped string in prose"
  status=1
fi
if grep -rnoE '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}' $targets \
   | grep -v 'rilambang@gmail.com'; then
  echo "✗ unexpected email address in prose"
  status=1
fi

[ "$status" -eq 0 ] && echo "✓ prose check clean"
exit $status
