# Monitor for Advent of Code Leaderboards

Monitor an Advent of Code leaderboard continuously and report earned stars via WhatsApp.

[Advent of Code](https://adventofcode.com/) is an Advent calendar made by [Eric Wastl](https://github.com/topaz) . It is made of small programming puzzles for a variety of skill sets and skill levels that can be solved in any programming language you like.

## How does it work?

Every 30 minutes the program iterates over all available years (events) of a private leaderboard, fetches its data and compares it to previously fetched data, stored as csv files in `/leaderboards`. Any detected changes are being sent with [PyWhatKit](https://github.com/Ankit404butfound/PyWhatKit) to a specifiable WhatsApp group chat.

## How to set up

- Make sure to have the needed python packages in `requirements.txt` installed on your machine
- Have a look at `connect.example.csv`, edit the connection details and rename the file to `connect.csv`. You need to provide your leaderboard id which you can find at the end of its URL, your [AOC session cookie](https://github.com/wimglenn/advent-of-code-wim/issues/1) and the [WhatsApp group chat id](https://medium.com/clicktochat/whatsapp-group-id-162d8101073c) you would like to send the messages to.
- Run `main.py`. During its first run, the program will automatically initialize all csv files in `/leaderboards`.