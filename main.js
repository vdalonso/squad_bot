const Discord = require('discord.js');
const fs = require('fs');//file system
//get token from local txt file.
const token = fs.readFileSync('./client_token.txt').toString(); 
const client = new Discord.Client( {intents: [Discord.Intents.FLAGS.GUILDS] });
const prefix = '-'; //Prefix is the symbol that will denote a command.
//create a list of commands availible to the bot.
client.commands = new Discord.Collection();
const commandFiles = fs.readdirSync('./commands/').filter(file => file.endsWith('.js'));
for(const file of commandFiles){
    const command = require(`./commands/${file}`);
    client.commands.set(command.name, command);
}
const queue = new Map();
const x = {
    a: 3,
    b: 5
}

// online message.
client.on('ready' , () => {
    console.log("Groovy2 is online!");
})

client.on('error', error => {
    console.error('The WebSocket encountered an error!!!!:', error);
    client.destroy();
    client.login(token);
});

client.on('shardError', error => {
	console.error('A websocket connection encountered an error:', error);
});

client.on('message' , message =>{
    // begin by ignoring all messages that don't start with our command prefix, or messages sent by bot.
    if (message.author.bot) return;
    if(!message.content.startsWith(prefix) || message.author.bot) return;
    const args = message.content.slice(prefix.length).split(" ");
    const command = args.shift().toLocaleLowerCase(); // command is the first word right after the prefix symbol.
    const serverQueue = queue.get(message.guild.id);
    //command check
    if(command === 'ping'){
        client.commands.get('ping').execute(message, args, x);
        //console.log(x);
    } else if (command === 'diceroll' || command === 'dice'){
        client.commands.get('diceroll').execute(message, args, Discord);
    } else if(command === 'play' || command ==='p'){
        //console.log(serverQueue)
        client.commands.get('play').execute(message, args, serverQueue, queue); //serverQueue is growing after every 'play' call, but not queue...
        //console.log(serverQueue)
    } else if(command === 'leave'){
        client.commands.get('leave').execute(message, args, serverQueue, queue);
    } else if(command === 'skip') {
        client.commands.get('skip').execute(message, serverQueue);
    } else if(command === 'help'){
        let x = ""; //[12]
        for(const i of client.commands.values()){
            x = x.concat(`-**${i.name}**..........${i.description}\n`)
        }
        message.channel.send(x);
    }
    else{message.channel.send("Unknown Command. please use '-help' for usage help. :)")}
} )

client.login(token);
