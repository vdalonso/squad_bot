const { execute } = require("./ping");

module.exports = {
    name: 'leave',
    description: 'remove the bot from voice channel.',
    async execute(message, args){
        const voiceChannel = message.member.voice.channel;
        if(!voiceChannel){ return message.channel.send("You must be in a voice channel to stop the music. ");}
        await voiceChannel.leave();
        await message.channel.send("Leaving voice channel!\nlater! :wave:")
    }
}