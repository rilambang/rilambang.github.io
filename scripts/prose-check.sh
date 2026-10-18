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

# Every image filename is a published URL, and cameras name files with a timestamp and
# an OS version. Check the *shape* of every tracked asset name — an allowlist, not a
# denylist, because the words worth blocking are the ones nobody can enumerate.
img_ext='webp|svg|png|jpe?g|gif|avif|mp4|webm'
shapes=$(git ls-files public docs | grep -iE "\.($img_ext)\$" \
         | grep -vE "/[a-z0-9]+(-[a-z0-9]+)*\.($img_ext)\$" || true)
if [ -n "$shapes" ]; then
  echo "✗ asset filename is not lowercase-hyphen, and it is a published URL:"
  echo "$shapes"
  status=1
fi

# Orphan check: an asset nothing references is either dead weight or a leak nobody sees.
# Read from a file, not a pipe — a piped while loop runs in a subshell and loses $status.
assets=$(mktemp)
git ls-files public | grep -iE "\.($img_ext)\$" > "$assets" || true
while IFS= read -r f; do
  n=$(basename "$f")
  if ! grep -rqF "$n" public docs --include='*.html' --include='*.js' --include='*.css' 2>/dev/null; then
    echo "✗ $f is referenced by no page — delete it or link it"
    status=1
  fi
done < "$assets"
rm -f "$assets"

[ "$status" -eq 0 ] && echo "✓ prose check clean"
exit $status
