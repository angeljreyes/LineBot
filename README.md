# Line Bot
Line is a multipurpose bot made specifically for spanish-speaking communities. You can invite Line to your Discord server with [this link](https://discord.com/oauth2/authorize?client_id=582009564724199434&scope=bot&permissions=277094067264).

## Features
### Utility
- Search for word definitions in Spanish and English
- Encode and decode from
  - Binary
  - Percent encoding
  - Morse code
- Get info from
  - Users
  - Servers
  - Roles
  - Channels
- Count characters and/or words in a text
- Get random numbers

### Fun
- Search for dad jokes
- Play TicTacToe against others or against the bot
- Ask the 8ball a question
- Let the bot describe you
- Make memes with AlexFlipnote API

### Text manipulation
- Change text to
  - Lowercase
  - Uppercase
  - Capitalized
  - Swap case
  - SaRcaSTiC
- Transform a text to emoji
- Replace words in a text
- Generate vaporwave/zero-width text

### Tags
- Opt-in tag system
- Mark tags as NSFW
- Gift tags
- Rename tags

## Prerequisites
- A Discord bot application (get one [here](https://discord.com/developers/applications))
- Python >= 3.12 (download [here](https://www.python.org/downloads/) and don't forget to check "Add Python to PATH" while installing!)

## Setup and Run
### 1. Clone the repository
```
git clone https://github.com/angeljreyes/LineBot.git
```
   
### 2. Move to the bot directory
```
cd LineBot
```
   
### 3. Setup and activate a virtual environment (optional but recommended).
On Windows:
```
py -m venv .venv
.venv\Scripts\activate
```
On Linux/MacOS:
```
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install the required Python dependencies
```
pip install -r requirements.txt
```
   
### 5. Run `setup.py` to setup the bot config file and create the databse
On Windows:
```
py setup.py
```
On Linux/MacOS:
```
python3 setup.py
```

### 6. Set the app token
Open `bot_conf.toml` with a text editor and, under the `[token]` table, set `stable` to your token. You can also read the "Configure the Bot" section below to learn more.
```toml
[token]
stable = "Stable token goes here" # This is the one used by default
dev = "Dev token goes here"
```

### 7. Run the bot
On Windows:
```
py src\run.py
```
On Linux/MacOS:
```
python3 src/run.py
```
**NOTE:** The bot should be ran from the Git root directory, as shown above. But running it from `src/` will automatically change the current working directory to the root directory, so feel free to run it from there if needed.

## Configure the Bot
Your bot configuration file is located at `bot_conf.toml`, this file is created based on `src/template_conf.toml`, so you can always check this one to see the defaults. Every setting is required to exist, but if you want to leave it empty, just set it to `0` or to an empty string `""` depending on the data type. Future updates may include new settings, so you might need to copy the new settings from `src/template_conf.toml`. Most settings have comments to show you how to use them, so if you wanna know more about them, just read the [config file](https://github.com/angeljreyes/LineBot/blob/main/src/template_conf.toml).

### Dev mode
The `dev_mode` setting, when enabled will use the guilds (guild = server) specified in `guilds` (guild IDs as a comma separated list of integers), as guild commands, so commands will only be available in these guilds, as opposed to making all commands global, which is rate limited to 200 per day. Dev mode will also show you hidden changelogs (see Changelogs and Versions) and won't add uses to the `commandstats` table in the database.

### Changelogs and Versions
The bot version is asigned in `src/core.py` as `bot_version`. This version will be used as the default version to show when using the `/changelog` command. Changelogs are stored on the database under the `changelog` table. You can use tools such as [DB Browser for SQLite](https://sqlitebrowser.org/) to view and change these values (or any data in the database for that matter). When the `hidden` field is set to `1`, that entry won't be visible for the stable version of the bot; you can use this to hide the changelogs of development versions of the bot while still storing your changes and being able to preview them.

## Contributing
You can report bugs or request new features and changes via issues or pull requests.
