#!/bin/bash
echo $(awk -F, '$1 ~ /^'"$1"'$/' ressources/l.txt)
