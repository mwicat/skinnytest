#!/bin/bash

set -o nounset

start_ext=$2
count=$1

echo "<include>"

for i in `seq 0 $((count - 1))`; do
    ext=$(( $start_ext + $i ))
    cat <<EOF
<user id="SEP$(printf '%012X' $i)">
   <skinny>
    <buttons>
      <button position="1" type="Line" label="Line 1" value="$ext" caller-name="User $ext"/>
    </buttons>
   </skinny>
  </user>
EOF
done

echo "</include>"
