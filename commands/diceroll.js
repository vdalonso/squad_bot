

const usage = "invalid dice arguement :( \nOptions include 'd4', 'd6', 'd10', 'd20'."
const die = ['d4', 'd6', 'd10', 'd20'];
module.exports = {
    name: 'diceroll',
    description: "rolls a  6 sided die, or d4, d10, or d20 if specified.",
    execute(message, args, Discord){
        let x;
        if(args.length === 0){ //case where user forgets to include arguements.
            x = Math.floor(Math.random() * (7 - 1) + 1);
            return message.channel.send(x.toString());
        } 
        else if (args.length === 1){    // case where user gives 1 arg.
            const d = args.shift();
            if( !die.includes(d) ){ // if arguement isnt one of the dice type, send error message.
                return message.channel.send(usage); 
            } 
            switch(d){
                case 'd4':
                    x = Math.floor(Math.random() * (5 - 1) + 1);
                    break;
                case 'd6':
                    x = Math.floor(Math.random() * (7 - 1) + 1);
                    break;
                case 'd10':
                    x = Math.floor(Math.random() * (11 - 1) + 1);
                    break;
                case 'd20':
                    x = Math.floor(Math.random() * (21 - 1) + 1);
                    break;
            }
            return message.channel.send(x.toString());
        } 
        else{return message.channel.send(usage); }
    }
}