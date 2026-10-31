<div align="center">

# dsh-travel-recon

> **Repositório oficial.** O único repositório oficial deste pacote, mantido por PerryLink. Repositórios com o mesmo nome em outras contas não são afiliados. Apache-2.0.

[![npm](https://img.shields.io/npm/v/dsh-travel-recon)](https://www.npmjs.com/package/dsh-travel-recon)
[![CI](https://github.com/PerryLink/dsh-travel-recon/actions/workflows/ci.yml/badge.svg)](https://github.com/PerryLink/dsh-travel-recon/actions)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE)
[![dsh-plugin](https://img.shields.io/badge/dsh--plugin-%E2%9C%93-green)](https://github.com/topics/dsh-plugin)
[![docs](https://img.shields.io/badge/docs-domain%20index-0b5fff)](https://perrylink.github.io/dsh-plugins/)
[![Gitee](https://img.shields.io/badge/Gitee-aggregate-c71d23?logo=gitee)](https://gitee.com/perrylink/dsh-plugins)
[![dshfind](https://dshfind.com/api/badge/PerryLink/dsh-travel-recon?metric=downloads)](https://dshfind.com/plugins/PerryLink/dsh-travel-recon?ref=badge)
[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)
[![Node](https://img.shields.io/badge/node-24.9%2B-brightgreen)](#)
[![npm downloads](https://img.shields.io/npm/dm/dsh-travel-recon)](https://www.npmjs.com/package/dsh-travel-recon)

**Ingestão de pedidos/faturas/cartões de viagem, deduplicação, conciliação tripla e registro.**

> **Status: alpha / sintético público / parcial / não contabilizado / não GA.** Sem evidência de clientes, dados de clientes ou promessa de produção.

[English](README.md) · [简体中文](README-zh.md) · [Español](README-es.md) · [Português](README-pt.md) · [हिन्दी](README-hi.md)

```sh
dsh plugin --profile <profile> add dsh-travel-recon
```

</div>

> ⭐ Se isso ajudar, uma estrela facilita a próxima pessoa encontrar. Nada fica bloqueado por ela.

![Workflow diagram for dsh-travel-recon: local input, plugin, local output.](docs/assets/dsh-travel-recon-flow.svg)

*Fluxo: entrada local → plugin → saída local. Não exige chamada a modelo.*

## Instalação

Instalar e verificar:

```sh
dsh plugin --profile <profile> add dsh-travel-recon
dsh --profile <profile> --dump-config | grep dsh-travel-recon
```

Desinstalar:

```sh
dsh plugin --profile <profile> remove dsh-travel-recon
```

## O que faz

Ingestão de pedidos/faturas/cartões de viagem, deduplicação, conciliação tripla e registro. Executa localmente no DeepSeek Harness. A tabela abaixo é a superfície exata de ferramentas; os exemplos usam a interface real.

Entrada e saída permanecem locais; nada é enviado.

## Ferramentas

Nomes e descrições de ferramentas ficam em inglês para corresponder à saída runtime.

| Ferramenta | Finalidade (em inglês) | Risco |
|---|---|---|
| `travel.ingest` | Ingest travel order/invoice/card rows | R1 local write |
| `travel.match` | Three-way match order/invoice/card | R0 |
| `travel.duplicate_check` | Detect duplicate invoice/card per trip | R0 |
| `travel.policy_check` | Read-only max-amount and invoice-presence policy check | R0 |
| `travel.export` | Export the reconciliation ledger xlsx | R1 local write |

## Início rápido

```sh
dsh plugin --profile <profile> add dsh-travel-recon
dsh --profile <profile> --dump-config | grep dsh-travel-recon
```

## Limites

- Apenas público/sintético; sem dados ou evidência de clientes.
- Alpha/parcial, não contabilizado, sem GA ou promessa de produção.
- Sem modelo ou rede, a menos que uma ferramenta indique.
- Os limites exatos estão na tabela e em `ACCEPTANCE.csv`.

## Amostra pública

As fixtures públicas/sintéticas ficam em `test/fixtures/`; `ACCEPTANCE.csv` registra as verificações com `counted=false`.

## Desenvolvimento

```sh
pnpm install --frozen-lockfile
pnpm build && pnpm lint && pnpm typecheck && pnpm test
```

## Compatibilidade

| Superfície | Status |
|---|---|
| Harness | `dsh >=0.2.1-rc.3 <0.3.0` |
| Node | `>=24.9.0 <25` |
| Platforms | All; local files only |
| Dados | No network, no model call, no upload |

## Permissões e dados

- Executa localmente; sem rede, sem modelo, sem upload.
- Apenas fixtures públicas/sintéticas; sem dados ou evidência de clientes.
- Alpha/parcial; não contabilizado, sem GA ou promessa de produção.
- Pacotes congelados continuam instaláveis; sem novos recursos, apenas falhas reais.

## Trabalho relacionado

Pacotes irmãos e índices da família: [dsh-einvoice](https://github.com/PerryLink/dsh-einvoice) · [dsh-bankrec](https://github.com/PerryLink/dsh-bankrec) · [dsh-ap-three-way](https://github.com/PerryLink/dsh-ap-three-way) · [dsh-finops-suite](https://github.com/PerryLink/dsh-finops-suite)

- [Índice de domínio](https://perrylink.github.io/dsh-plugins/)
- [Família de checkers](https://perrylink.github.io/zh/checkers/)
- [Família principal](https://github.com/PerryLink/dsh-kit)
- [Scenario article](https://perrylink.github.io/dsh-plugins/articles/finops-suite.html)

## Família

<details>
<summary>Família de plugins DSH (15 pacotes + 2 suites)</summary>

| Package | npm |
|---|---|
| **[dsh-einvoice](https://github.com/PerryLink/dsh-einvoice)** | [npm](https://www.npmjs.com/package/dsh-einvoice) |
| **[dsh-docx-redline](https://github.com/PerryLink/dsh-docx-redline)** | [npm](https://www.npmjs.com/package/dsh-docx-redline) |
| **[dsh-policy-ledger](https://github.com/PerryLink/dsh-policy-ledger)** | [npm](https://www.npmjs.com/package/dsh-policy-ledger) |
| **[dsh-ghg](https://github.com/PerryLink/dsh-ghg)** | [npm](https://www.npmjs.com/package/dsh-ghg) |
| **[dsh-bankrec](https://github.com/PerryLink/dsh-bankrec)** | [npm](https://www.npmjs.com/package/dsh-bankrec) |
| **[dsh-ap-three-way](https://github.com/PerryLink/dsh-ap-three-way)** | [npm](https://www.npmjs.com/package/dsh-ap-three-way) |
| **[dsh-ifc-qto](https://github.com/PerryLink/dsh-ifc-qto)** | [npm](https://www.npmjs.com/package/dsh-ifc-qto) |
| **[dsh-qms-capa](https://github.com/PerryLink/dsh-qms-capa)** | [npm](https://www.npmjs.com/package/dsh-qms-capa) |
| **[dsh-legal-intake](https://github.com/PerryLink/dsh-legal-intake)** | [npm](https://www.npmjs.com/package/dsh-legal-intake) |
| **[dsh-legal-clause](https://github.com/PerryLink/dsh-legal-clause)** | [npm](https://www.npmjs.com/package/dsh-legal-clause) |
| **[dsh-freight-audit](https://github.com/PerryLink/dsh-freight-audit)** | [npm](https://www.npmjs.com/package/dsh-freight-audit) |
| **[dsh-hs-candidate](https://github.com/PerryLink/dsh-hs-candidate)** | [npm](https://www.npmjs.com/package/dsh-hs-candidate) |
| **[dsh-travel-recon](https://github.com/PerryLink/dsh-travel-recon)** | [npm](https://www.npmjs.com/package/dsh-travel-recon) |
| **[dsh-pim-lint](https://github.com/PerryLink/dsh-pim-lint)** | [npm](https://www.npmjs.com/package/dsh-pim-lint) |
| **[dsh-eval-pack](https://github.com/PerryLink/dsh-eval-pack)** | [npm](https://www.npmjs.com/package/dsh-eval-pack) |
| **[dsh-finops-suite](https://github.com/PerryLink/dsh-finops-suite)** | [npm](https://www.npmjs.com/package/dsh-finops-suite) |
| **[dsh-contract-suite](https://github.com/PerryLink/dsh-contract-suite)** | [npm](https://www.npmjs.com/package/dsh-contract-suite) |

</details>

## Licença

Apache-2.0. See `LICENSE`, `NOTICE`, `THIRD-PARTY-NOTICES`.
