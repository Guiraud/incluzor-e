#!/bin/bash
echo $(awk -F, '$1 ~ /^'"$1"'$/' lex.txt)
