#!/bin/bash
for line in $(cat texte_a_plat.txt); do ./cherche.sh $line ; done  
