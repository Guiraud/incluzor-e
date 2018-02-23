<html><head></head>
<body>
<form method="post" action="essai.php">
<p>
    On insèrera ici les éléments de notre formulaire.
</p>
<input type="text" name="texte" />
<input type="submit" value="Valider" />
</form>
<?php 
echo "ton texte est : ".$_POST['texte'];
exec("/usr/bin/python script.py", $variable);
echo $variable[0];?>
</body>
</html
