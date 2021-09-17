const Discord = require('discord.js');
const client = new Discord.Client( {intents: ['GUILDS', 'GUILD_MESSAGES'] });
const prefix = '-'; //Prefix is the symbol that will denote a command.
//file system.
const fs = require('fs');
//create a list of commands availible to the bot.
client.commands = new Discord.Collection();
const commandFiles = fs.readdirSync('./commands/').filter(file => file.endsWith('.js'));
for(const file of commandFiles){
    const command = require(`./commands/${file}`);
    client.commands.set(command.name, command);
}
const queue = new Map();

// online message.
client.on('ready' , () => {
    console.log("Groovy2 is online!");
})

client.on('error', error => {
    console.error('The WebSocket encountered an error:', error);
});

client.on('message' , message =>{
    // begin by ignoring all messages that don't start with our command prefix, or messages sent by bot.
    if(!message.content.startsWith(prefix) || message.author.bot) return;
    const args = message.content.slice(prefix.length).split(" ");
    const command = args.shift().toLocaleLowerCase(); // command is the first word right after the prefix symbol.
    //command check
    if(command === 'ping'){
        client.commands.get('ping').execute(message, args);
    } else if (command === 'diceroll' || command === 'dice'){
        client.commands.get('diceroll').execute(message, args, Discord);
    } else if(command === 'play' || command ==='p'){
        const serverQueue = queue.get(message.guild.id);
        client.commands.get('play').execute(message, args, serverQueue, queue);
    } else if(command === 'leave'){
        client.commands.get('leave').execute(message, args);
    } else if(command === 'help'){ // TODO: check
        let x = "";
        for(const i of client.commands.values()){
            x = x.concat(`-**${i.name}**..........${i.description}\n`)
        }
        message.channel.send(x);
    }
    else{message.channel.send("Unknown Command. please use '-help' for usage help. :)")}
} )

client.login('NTcxODI3MTIxNzYxMTU3MTQw.XMTZgQ.7fUuNWBMrYqkjJdSsJNv_DpW9ds');