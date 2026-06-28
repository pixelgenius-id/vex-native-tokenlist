# VEX Native Token List

Official token list for VEX native chain (EOSIO/eosio.token standard). PR-based listing with automated validation.

**Token List URL:**
```
https://raw.githubusercontent.com/YudaAdiPratama/vex-native-tokenlist/main/tokenlist.json
```

## Submit a Token

1. Fork this repo
2. Add your token to `tokenlist.json`
3. Add logo to `assets/<SYMBOL>.png`
4. Submit a Pull Request

## Listing Requirements

| Requirement | Detail |
|-------------|--------|
| Chain | VEX native (EOSIO) |
| Contract | eosio.token standard (`transfer`, `issue`, `create` actions) |
| Token created | Must have active supply (`get_currency_stats` returns data) |
| Contract age | Minimum **7 days** since `create` action |
| Logo | **256×256px PNG**, max **50KB**, named `<SYMBOL>.png` |
| Symbol | Uppercase letters only (e.g. `SPARK`) |

## tokenlist.json Entry Format

```json
{
  "contract": "yourcontract",
  "symbol": "SYM",
  "precision": 4,
  "name": "Token Full Name",
  "logoURI": "https://raw.githubusercontent.com/YudaAdiPratama/vex-native-tokenlist/main/assets/SYM.png"
}
```

## PR Review Process

1. GitHub Actions runs automated checks on every PR:
   - Account exists on VEX native chain
   - ABI contains eosio.token standard actions
   - Token has been created (supply exists)
   - Contract age ≥ 7 days
   - Logo is 256×256px PNG, max 50KB
   - No existing tokens removed
2. All checks must pass (green)
3. Maintainer does manual review
4. If approved → merged

## Resources

- [SPARK Swap](https://swap.nodespark.fun)
- [VEX Explorer](https://vexascan.com)
- [VEX Native Chain API](https://vexascan.com/v1/chain/get_info)
