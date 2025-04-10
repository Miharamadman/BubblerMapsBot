# BubblerMapsBot 

A Telegram bot that provides detailed token analysis using Bubblemaps and DexScreener data. The bot offers insights into token holder distribution, market metrics, and decentralization scores.

## Features 

- **Token Analysis**
  - Holder distribution and concentration metrics
  - Decentralization score calculation
  - Top holder analysis with transaction counts
  - Smart contract holder identification

- **Market Data**
  - Current price and market cap
  - Liquidity information
  - Price changes (1H, 24H)

- **Multi-Chain Support**
  - Ethereum (ETH)
  - Binance Smart Chain (BSC)
  - Fantom (FTM)
  - Avalanche (AVAX)
  - Arbitrum (ARBI)
  - Polygon (POLY)
  - Base
  - Solana (SOL)

## Installation 🛠️

1. Clone the repository:
```bash
git clone https://github.com/yourusername/BubblerMapsBot.git
cd BubblerMapsBot
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with the following variables:
```env
BUBBLER_TOKEN=your_telegram_bot_token
SCREENSHOT_API_TOKEN=your_screenshot_machine_api_key
```

## Dependencies 

- Python 3.7+
- pyTelegramBotAPI==4.15.2
- requests==2.31.0
- python-dotenv==1.0.0

## Usage 

1. Start the bot:
```bash
python main.py
```

2. In Telegram, interact with the bot using these commands:
- `/start` - Initialize the bot
- `/help` - Display help information
- `/getinfo [chain] [address]` - Get token analysis

Examples:
```
/getinfo eth 0x123...abc
/getinfo bsc 0x456...def
```

## Methodology 

### Decentralization Score
The bot calculates a decentralization score based on token holder concentration:
- Analyzes the top 20 holders' total percentage
- Score = 100 - (top_20_concentration / 2)
- Higher scores indicate better decentralization
- 🟢 70-100: Good decentralization
- 🟡 40-69: Moderate decentralization
- 🔴 0-39: Poor decentralization

### Holder Analysis
For each top holder, the bot shows:
- Percentage of total supply held
- Number of transactions
- Whether the holder is a smart contract
- Ranking (👑 Top holder, 🥈 Second, 🥉 Third)

### Data Sources
- **Bubblemaps API**: Holder distribution and transaction data
- **DexScreener API**: Market data, pricing, and liquidity information

## Rate Limiting 

- 10 requests per minute per user
- Helps prevent API abuse and ensures service stability

## Error Handling 

The bot handles various error scenarios:
- Invalid addresses
- Unsupported chains
- API failures
- Rate limit exceeded

## Contributing 

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License 

[MIT License](LICENSE)

## Disclaimer 

This bot is for informational purposes only. Always do your own research (DYOR) before making any investment decisions. The data provided may not be 100% accurate and should be verified from multiple sources. 