# Discord Crypto Tracker Bot
Discord bot written in [Python](https://www.python.org/) using [discord.py](https://discordpy.readthedocs.io/en/stable/) for tracking information about the cryptocurrencies  

API from [CoinGecko](https://www.coingecko.com/en/api/documentation) was used to fetch the data

## Prerequisites
* `.env` file
  > Provide `TOKEN` variable obtained from Discord developer portal

* `venv`
  > Before installing dependencies it is highly recommended to work in [virtual environment](https://docs.python.org/3/library/venv.html).
  > If you want to create virtual environment `.venv`, use following command:
  > ```bash
  >  python -m venv .venv
  >  ```
  > Make sure it is activated after installation

## Install dependencies
```bash
pip install -r requirements.txt
```

## Usage
* Command `python main.py`
  > This command initiates the bot using file logging. The bot's activities, errors, and relevant information will be logged into a file named `discord.log`.
  > File logging has advantages for long-term record-keeping, troubleshooting, and maintaining a history of the bot's performance.
  > Keep in mind that file logging may accumulate data over time, so regular maintenance might be needed to manage log files.

* Command `python main.py --test`
  > This command starts the bot in testing mode, utilizing standard console logging. When initiated with the --test flag, the bot will log information
  > directly to the console instead of a file. Console logging is useful during testing and development phases, providing immediate feedback and visibility into the bot's activities.

## Commands
<table>
  <tr>
    <th>Command</th>
    <th>Explanation</th>
  </tr>
  <tr>
    <td>$sync</td>
    <td>Syncing slash commands with the guild</td>
  </tr>
  <tr>
    <td>/ath [coin]</td>
    <td>All time high for the coin</td>
  </tr>
  <tr>
    <td>/info [coin]</td>
    <td>Basic info for the coin (market cap, price, 24h change etc.)</td>
  </tr>
  <tr>
    <td>/pnl [coin] [type] [price]</td>
    <td>Profit and loss for the coin based on type of the position and the price when position was opened</td>
  </tr>
  <tr>
    <td>/price_change [coin]</td>
    <td>Price change (24h, 7 days, 14 days, 30 days)</td>
  </tr>
  <tr>
    <td>/price [coin]</td>
    <td>Price of the coin</td>
  </tr>
  <tr>
    <td>/top [n]</td>
    <td>Top n coins by the market cap</td>
  </tr>
</table>
