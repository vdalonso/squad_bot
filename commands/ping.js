module.exports = {
    name: 'ping',
    description: "check if i'm alive! :D",
    execute(message, args){
        message.channel.send('pong!');
    }
}