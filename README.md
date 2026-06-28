# VEX Native Token List

Official token list for VEX native chain (eosio.token standard). PR-based listing with automated validation.

**Token List URL:**
```
https://raw.githubusercontent.com/pixelgenius-id/vex-native-tokenlist/main/tokenlist.json
```

---

## How to Submit Your Token

### Step 1 — Fork this repo

Click the **Fork** button at the top right of this page, then clone your fork:

```bash
git clone https://github.com/YOUR_USERNAME/vex-native-tokenlist.git
cd vex-native-tokenlist
```

### Step 2 — Prepare your logo

- Format: **PNG**
- Size: exactly **256×256 px**
- Max file size: **50 KB**
- Filename: your token symbol in **uppercase** + `.png`

Example: for token `MYTKN`, the file must be named:
```
MYTKN.png
```

Place the file in the `assets/` folder:
```
assets/
  MYTKN.png
```

### Step 3 — Add your token to `tokenlist.json`

Add a new entry inside the `"tokens"` array:

```json
{
  "contract": "yourcontract",
  "symbol": "MYTKN",
  "precision": 4,
  "name": "Your Token Full Name"
}
```

> **Do not add `logoURI`** — it will be set automatically after your PR is merged.
> If you include `logoURI`, the validation will fail.

> Symbol must be **uppercase letters only** (e.g. `VEX`, `USDT`, `SPARK`).

### Step 4 — Submit a Pull Request

Push your changes and open a PR against the `main` branch of this repo. GitHub Actions will automatically run validation checks and post the result as a comment on your PR.

---

## Listing Requirements

| Requirement | Detail |
|-------------|--------|
| Chain | VEX native chain |
| Contract standard | Must implement eosio.token (`transfer`, `issue`, `create` actions) |
| Token created | Must have active supply (`get_currency_stats` returns data) |
| Contract age | Minimum **7 days** since `create` action |
| Logo file | PNG, exactly **256×256 px**, max **50 KB** |
| Logo filename | `assets/<SYMBOL>.png` (uppercase) |
| Symbol format | Uppercase letters only |

---

## Automated Validation

When you open a PR, GitHub Actions automatically checks:

- JSON is valid and all required fields are present
- Contract account exists on VEX native chain
- Contract ABI contains standard eosio.token actions (`transfer`, `issue`, `create`)
- Token has been created and has active supply
- Contract was deployed at least 7 days ago
- Logo exists at `assets/<SYMBOL>.png`, is exactly 256×256 px, PNG format, and ≤ 50 KB
- No existing tokens were removed from the list

All checks must pass before a maintainer will review your PR.

---

## After Merge

Once your PR is merged, your token will automatically appear in:
- **VEXascan** native token list
- **SPARK Swap** token selector (if applicable)

No additional steps needed.

---

## Resources

- [SPARK Swap](https://swap.nodespark.fun)
- [VEXascan Explorer](https://vexascan.com)
- [VEX Chain API](https://vexascan.com/v1/chain/get_info)
