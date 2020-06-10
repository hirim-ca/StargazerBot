# StargazerBot
 A discord bot that has a rankable starboard.

Current version: 0.1

**Disclaimer: This bot was made for personal use and was not programmed for multi-server use. Please add server detection mechanism if you are planning to host the bot in multiple servers.**

## List of Commands

### Modlue *Stargazer*

 - `starChannel` - (Admin only) Show the current starboard channel.
 - `starChannel [#channel]` - (Admin only) Set the starboard channel to `[#channel]`.
 - `rankQuote` - Displays top quotes sorted by scores.
 - `rankAuthor` - Displays top authors sorted by their total scores.
 - `feature [@user]` - Sends a random quote from user.
 - `describe [@user]` - Checks the user's quote status.

---

### Modlue *Backdoor*

 - `getMessageInChannel [#channel] [limit] [output_filename]`: (Dev only) Export `[limit]` number of messages in the specified channel to output. Setting limit=-1 will export all messages.
 - `dbStatus`: (Dev only) Check database status.
 - `clearChannel [#channel] [limit]`: (Admin only) Purge `[limit]` number of messages from channel specified. Setting limit=-1 will purge all messages.
 
## Changelog

0.1
 - The initial version.
