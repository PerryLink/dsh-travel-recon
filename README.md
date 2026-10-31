# dsh-travel-recon

Travel order/invoice/card ingest, dedupe, three-way match, read-only policy check and ledger export for DeepSeek Harness.

> **Status: alpha / public-synthetic / partial / not counted / not GA.** No customer evidence, customer data, or production-readiness claim. All acceptance rows are `counted=false`.

## Install

```sh
dsh plugin --profile <profile> add dsh-travel-recon
dsh --profile <profile> --dump-config | grep dsh-travel-recon
```

Requires DSH `>=0.2.1-rc.3 <0.3.0` and Node `>=24.9 <25`.

<details>
<summary>中文摘要</summary>

差旅订单/发票/卡流水对账、去重、只读政策检查与台账导出。 安装：`dsh plugin --profile <profile> add dsh-travel-recon`。公开/合成、alpha、非 GA。

</details>

## Tools

| Tool | What it does | Risk |
|---|---|---|
| `travel.ingest` | Ingest travel order/invoice/card rows | R1 local write |
| `travel.match` | Three-way match order/invoice/card | R0 |
| `travel.duplicate_check` | Detect duplicate invoice/card per trip | R0 |
| `travel.policy_check` | Read-only max-amount and invoice-presence policy check | R0 |
| `travel.export` | Export the reconciliation ledger xlsx | R1 local write |

## Input / output

**Input:** travel order, invoice and card rows. **Output:** matched/unmatched rows, duplicate findings, read-only policy findings, and an xlsx ledger.

## Configuration

| Env | Default | Meaning |
|---|---|---|
| `DSH_TRAVEL_HOME` | `$DSH_HOME/storages/dsh-travel-recon` | local domain and exports |

## Limits / non-claims

- No OTA/airline/hotel adapters, PDF/OCR invoice extraction, or policy engine.
- Policy checks are read-only; no approval, rejection, or reimbursement posting.
- No Client surface and no customer traveler data.
- No customer evidence, customer data, or production-readiness claim; all fixtures are public/synthetic.

## Public sample

Synthetic travel order/invoice/card fixtures; `ACCEPTANCE.csv` lists 5 public checks.

## Development

```sh
pnpm install --frozen-lockfile
pnpm build && pnpm lint && pnpm typecheck && pnpm test && pnpm gate:sku15
```

## License

Apache-2.0. See `LICENSE`, `NOTICE`, `THIRD-PARTY-NOTICES`.
