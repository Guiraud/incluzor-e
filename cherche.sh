#!/bin/bash
echo $(awk -F, '$2 ~ /^'"$1"'$/' ressources/l.txt)
