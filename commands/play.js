const ytdl = require('ytdl-core');
const ytSearch = require('yt-search');
const { joinVoiceChannel } = require('@discordjs/voice');

module.exports = {
    name: 'play',
    description: "joins voice channel and plays specified song.",
    async execute(message, args, serverQueue, queue){
        const voiceChannel = message.member.voice.channel;
        //user not in VC check
        if(!voiceChannel){return message.channel.send('please be in a channel to execute this command!')}
        //arg check, if no arguement send ERROR
        if(!args.length){ return message.channel.send("please send a second arguement like a song name or video link!")}
        let song = null;
        if(ytdl.validateURL(args[0])){ // check if arg is a URL.
            const songInfo = await ytdl.getInfo(args[0]);
            song = {
                title: songInfo.videoDetails.title,
                url: args[0]
            };
        } else{ // case where arg is NOT a url.
            const videoResult = await ytSearch(args.join(' '));
            const vid = (videoResult.videos.length > 1) ? videoResult.videos[0] : null;
            song = {
                title: vid.title,
                url: vid.url
            };
        }
        if(!serverQueue){ // if queue is empty
            const queueConstruct = {
                textChannel: message.channel,
                voiceChannel: voiceChannel,
                connection: null,
                songs: [],
                volume: 5,
                playing: true
            };
            this.serverQueue = queueConstruct;
            queue.set(message.guild.id, queueConstruct);
            queueConstruct.songs.push(song);
            try {
                var connection = await voiceChannel.join();
                queueConstruct.connection = connection;
                this.playSong(message.guild, song, queue);
            } catch (err){
                console.log(err);
                queue.delete(message.guild.id);
                return message.channel.send(err);
            }

        } else {
            serverQueue.songs.push(song);
            return message.channel.send(`***${song.title}*** has been added to the queue :)`);
        }
    },
    playSong(guild, song, queue){
        const serverQueue = queue.get(guild.id);
        //console.log("from playSong method"+ serverQueue);
        if (!song) {
          serverQueue.voiceChannel.leave();
          queue.delete(guild.id);
          return;
        }
        const disp = serverQueue.connection
            .play(ytdl(song.url, {filter: 'audioonly'}))
            .on("finish", () =>{
                serverQueue.songs.shift();
                this.playSong(guild, serverQueue.songs[0], queue);
            })
            .on("error", error => console.error(error));
        disp.setVolumeLogarithmic(serverQueue.volume / 5);
        serverQueue.textChannel.send(`Now Playing: ***${song.title}***`);
    }
}