#!/bin/sh

for filename in $(find . -name appDuration.txt | sort); do
  aux=$(echo "$filename" | sed -e 's/appDuration/aux/g')
  awk '$1 < 0 { x = 24 * 60 * 60 * 1000 + $1; print x "\t" $2; next } { print }' \
    < "$filename" > "$aux"
  mv "$aux" "$filename"
done
