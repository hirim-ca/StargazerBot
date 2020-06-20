# StargazerBot
 A discord bot that has a rankable starboard.

Current version: 0.1

**Disclaimer: This bot was made for personal use and was not programmed for multi-server use. Please add server detection mechanism if you are planning to host the bot in multiple servers.**

## List of Commands

### English

#### Module *Stargazer*

 - `stChn` - (Admin only) Show the current starboard channel.
 - `stChn [#channel]` - (Admin only) Set the starboard channel to `[#channel]`.
 - `rkQt` - Displays top quotes sorted by scores.
 - `rkAt` - Displays top authors sorted by their total scores.
 - `rand` - Sends a random quote.
 - `rand [@user]` - Sends a random quote from user.
 - `desc [@user]` - Checks the user's quote status.

#### Module *ServerData*

 - `getMsg [#channel] [limit] [output_filename]`: (Dev only) Export `[limit]` number of messages in the specified channel to output. Setting limit=-1 will export all messages.
 - `clChn [#channel] [limit]`: (Admin only) Purge `[limit]` number of messages from channel specified. Setting limit=-1 will purge all messages.

---

### 中文

#### *Stargazer* 模組

 - `stChn` - (管理員專用) 顯示目前的名言頻道。
 - `stChn [#channel]` - (管理員專用) 設定新的名言頻道為`[#channel]`。
 - `rkQt` - 顯示名言排行榜。
 - `rkAt` - 顯示用戶名言總分數排行榜。
 - `rand` - 隨機挑選一條名言。
 - `rand [@user]` - 隨機挑選一條`[@user]`的名言。
 - `desc [@user]` - 查看用戶的名言信息。

#### *ServerData* 模組

 - `getMsg [#channel] [limit] [output_filename]`: 將頻道內`[limit]`數量的訊息截取。將`[limit]`設為-1則截取該頻道全部的訊息。(limit > 100 or -1 為管理員專用)
 - `clChn [#channel] [limit]`: (管理員專用) 將頻道內近期`[limit]`數量的訊息刪除。將上限數設為-1則刪除該頻道全部的訊息。


## Changelog

0.1.1
 - Shotened function names for ease of use.
 - getMsg can now be used for all users and sends the output as a file upload.
 - Seperated server datamining functions to a new cog named ServerData.
 - Added `ServerData.getAc`.
 - Modified `Stargazer.feature`.
 - Code optimization and bug fixes.

0.1
 - The initial version.
