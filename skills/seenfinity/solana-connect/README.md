# OpenClaw Solana Connect v2.0

> The missing link between OpenClaw agents to Solana blockchain
> **Now using @solana/kit (Solana Web3.js v2)**

A purpose-built toolkit that enables autonomous AI agents running on OpenClaw to interact seamlessly with the Solana blockchain.

## ⚠️ IMPORTANT: Current Limitations

**This is a READ-ONLY toolkit for now.**

| Function | Status | Description |
|----------|--------|-------------|
| `getBalance()` | ✅ Works | Read SOL/token/NFT balances |
| `getTransactions()` | ✅ Works | Read transaction history |
| `getTokenAccounts()` | ✅ Works | Read token holdings |
| `generateWallet()` | ✅ Works | Generate new addresses |
| `connectWallet()` | ✅ Works | Validate addresses |
| `sendSol()` | ⚠️ Simulation Only | Cannot send real transactions |

**Signing is not yet implemented.** You can simulate transactions but cannot send real transactions.

## 🛡️ Security: Private Keys Are Protected

**This toolkit NEVER returns private keys to the agent.**

- `connectWallet()` returns only the address
- `generateWallet()` returns only the address  
- Transactions are signed internally without exposing the raw private key

This prevents prompt injection attacks where a compromised agent could exfiltrate private keys.

### Always Use Testnet First

```bash
# Set testnet RPC for development (RECOMMENDED)
export SOLANA_RPC_URL=https://api.testnet.solana.com

# Only switch to mainnet after thorough testing
export SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
```

### Best Practices

1. **Use a Dedicated Wallet** — Never use your main wallet. Create a separate wallet with limited funds for agent trading.

2. **Set Spending Limits** — Configure maximum transaction amounts:
   ```bash
   export MAX_SOL_PER_TX=10      # Max 10 SOL per transaction
   export MAX_TOKENS_PER_TX=1000 # Max 1000 tokens per transaction
   ```

3. **Enable Dry Run Mode** — Test transactions before sending:
   ```javascript
   const result = await sendSol(wallet, toAddress, amount, { dryRun: true });
   ```

4. **Store Private Keys Securely** — Use environment variables, never hardcode:
   ```javascript
   // ✅ Good
   const wallet = await connectWallet(process.env.AGENT_PRIVATE_KEY);
   
   // ❌ Bad - never do this
   const wallet = await connectWallet('your-private-key-here');
   ```

5. **Monitor Activity** — Regularly review transaction history and wallet balances.

---

## Features

- 🧠 **AI-First Design** — Built for autonomous agents
- 🔄 **OpenClaw Native** — Works out of the box with OpenClaw skills
- 🤖 **Agent-Friendly** — Natural language inputs, automatic validation
- 🛡️ **Secure by Default** — Sandboxed transactions, amount limits, dry-run mode

### Wallet Operations
- Generate new wallets
- Connect existing wallets
- Check balances (SOL, tokens, NFTs)
- Transaction history

### Transaction Operations
- Send SOL
- Send SPL tokens
- Dry-run mode (simulate before send)

### Token Operations
- Get token balances
- Get NFT holdings
- Token metadata

---

## Installation

```bash
# Install via ClawHub
clawhub install solana-connect

# Or clone manually
git clone https://github.com/Seenfinity/openclaw-solana-connect.git
cd solana-connect
npm install
```

---

## Quick Start

```javascript
const { connectWallet, getBalance, sendSol } = require('./scripts/solana.js');

// Connect with a private key (only address is returned - private key stays internal)
const wallet = await connectWallet(process.env.AGENT_PRIVATE_KEY);

// Check balance using the address
const balance = await getBalance(wallet.address);

// Send SOL (dry-run mode - simulation only by default)
// Private key is used internally for signing, never exposed
const result = await sendSol(process.env.AGENT_PRIVATE_KEY, toAddress, 1.0, { dryRun: true });
console.log('Simulation:', result);

// NOTE: Real transactions require additional security measures
// See Security section below
```

---

## Configuration

```bash
# Required: RPC endpoint
export SOLANA_RPC_URL=https://api.testnet.solana.com

# Optional: Security limits
export MAX_SOL_PER_TX=10
export MAX_TOKENS_PER_TX=1000
```

---

## Testing

```bash
npm install
node test.js
```

All tests pass:
- ✅ Generate wallet
- ✅ Connect to Solana RPC
- ✅ Get balance
- ✅ Get token accounts
- ✅ Get transactions

---

## Documentation

See [SKILL.md](./SKILL.md) for full documentation.

---

## GitHub

[github.com/Seenfinity/openclaw-solana-connect](https://github.com/Seenfinity/openclaw-solana-connect)

---

## License

MIT © 2026 Seenfinity

---

*Built for OpenClaw agents. Powered by Solana.*
