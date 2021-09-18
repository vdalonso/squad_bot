module.exports = {
    name: 'ping',
    description: "check if i'm alive! :D",
    execute(message, args, x){
        x.a = 1;
        x.b = 11;
        message.channel.send('pong!');
    }
}