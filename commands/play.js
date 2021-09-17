const ytdl = require('ytdl-core');
const ytSearch = require('yt-search');
const { joinVoiceChannel } = require('@discordjs/voice');

module.exports = {
    name: 'play',
    description: "Joins and plays",
    async execute(message, args, serverQueue, queue){
        const voiceChannel = message.member.voice.channel;
        //user not in VC check
        if(!voiceChannel){return message.channel.send('please be in a channel to execute this command!')}
        //arg check
        if(!args.length){ return message.channel.send("please send a second arguement like a song name or video link! (URL-only right now, srry! -mang0)")}
        // TEMP: arg is URL check.
        //const videoResult = await ytSearch(query);
        //return (videoResult.videos.length > 1) ? videoResult.videos[0] : null; // return only the first video result
        if(!ytdl.validateURL(args[0])){
            
            return message.channel.send("please send a YouTube URL!")
        }
        //TODO: search is only working for url's. change so it can be either query or url.
        const songInfo = await ytdl.getInfo(args[0]);
        const song = {
            title: songInfo.videoDetails.title,
            url: args[0]
        };
        if(!serverQueue){
            const queueConstruct = {
                textChannel: message.channel,
                voiceChannel: voiceChannel,
                connection: null,
                songs: [],
                volume: 5,
                playing: true
            };
            queue.set(message.guild.id, queueConstruct);
            queueConstruct.songs.push(song);
            //console.log(song.title); // url is for some reason 'undefined'
            try {
                var connection = await voiceChannel.join();
                queueConstruct.connection = connection;
                //play
                this.playSong(message.guild, song, queue);
            } catch (err){
                console.log(err);
                queue.delete(message.guild.id);
                return message.channel.send(err);
            }

        } else {
            serverQueue.songs.push(song);
            return message.channel.send(`${song.title} has been added to the queue :)`);
        }
        /*
        //function that returns a video url given a query.
        const videoFinder = async (query) => {
            const videoResult = await ytSearch(query);
            return (videoResult.videos.length > 1) ? videoResult.videos[0] : null; // return only the first video result.

        }
        const video = await videoFinder(args.join(' '))
        if(video){
            const stream = ytdl(video.url, {filter: 'audioonly'}); // actual audio
            connection.play(stream, {seek: 0, volume: 1})
            .on('finish', () => {
                voiceChannel.leave();
            });
            await message.reply(`Now Playing ***${video.title}***`)
        } else{
            message.channel.send("No results found");
        }*/
    },
    playSong(guild, song, queue){
        const serverQueue = queue.get(guild.id);
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