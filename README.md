# Discord Crypto Tracker Bot
Discord bot written in [Python](https://www.python.org/) using [discord.py](https://discordpy.readthedocs.io/en/stable/) for tracking information about the cryptocurrencies  

API from [CoinGecko](https://www.coingecko.com/en/api/documentation) was used to fetch the data

## Requirements
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install requirements

```bash
pip3 install -r requirements.txt
```

## Usage
Before using the bot create `.env` file and provide the `TOKEN` variable

Example of `.env` file:
```txt
TOKEN = 'YOUR_TOKEN_HERE'
```

## Logging
  - If you want to test the bot locally and be able to use terminal log start the script using `python main.py --test`
  - If you want to use the bot on the server with log file start the script using `python main.py`

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
