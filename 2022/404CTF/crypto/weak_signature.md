# Crypto / Weak Signature
Points: 1000
Difficulté: Facile

# Énoncé

Un nouveau système a été mis en place pour exécuter du code de façon sécurisée sur l'infrastructure. Il suffit d'envoyer une archive signée et encodée en base 64 pour exécuter le code Python qu'elle contient !

Vous trouverez la documentation de ce système et un exemple en pièces jointes. Tentez de voir si vous ne pourriez pas l'exploiter afin de lire le précieux fichier flag.txt

Auteur : Cyxo#0458

`nc challenge.404ctf.fr 32441`

# Résolution
Une faiblesse simple dans les signatures est la checksum du fichier à signer. Ici la fonction semble exploitable et donc on doit pouvoir trouver un fichier qui a le même checksum que l'original et bruteforçant les valeurs. Dans cette logique on peut compléter un payload en faisant la différence de valeur du checksum avec sa valeur actuelle et en complétant avec des caractères qui ont le bon total. Ensuite il ne reste plus qu'à recréer un fichier avec la commande que l'on souhaite et la signature originale. 

```python
def checksum(data: bytes) -> int:
    # Sum the integer value of each byte and multiply the result by the length
    chksum = sum(data) * len(data)

    return chksum
def complete(data: bytes, size: int, sm: int):
    n = size - len(data) - 1
    sm -= sum(data)
    c = chr(int(sm/n)) 
    for i in range(n):
        data += c.encode("utf-8")
        sm -= ord(c)
    data += chr(sm).encode("utf-8")
    return data
```

