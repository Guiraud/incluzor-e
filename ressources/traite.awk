awk -F $"\t" '{if (NR > 16) print $2,$4}' lexique-dicollecte-fr-v6.2.txt > lex.txt
awk -F, '$1 ~ /^demandé$/' lex.txt

sed  's/\"//g' file.csv
sed  's/\"//g' file.csv | awk -F" " '$1'
sed  's/\"//g' file.csv | awk -F" " '$1' | sed 's/ /\n/g' > texte_a_plat.txt
