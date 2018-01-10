awk -F $"\t" '{if (NR > 16) print $2,$4}' lexique-dicollecte-fr-v6.2.txt | head
sed  's/\"//g' file.csv
