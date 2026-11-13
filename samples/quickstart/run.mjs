#!/usr/bin/env node
/**
 * Quickstart runner for the shipped synthetic sample.
 *
 *   node samples/quickstart/run.mjs          # human-readable transcript (screenshot source)
 *   node samples/quickstart/run.mjs --json   # canonical result used as the gold file
 *
 * Everything runs locally against `samples/quickstart/input/`; nothing is uploaded and no
 * customer data is involved. The export is written to a temporary directory that is removed
 * afterwards, so the sample never writes into the checkout.
 */
import { createHash } from 'node:crypto'
import { mkdtemp, readFile, rm } from 'node:fs/promises'
import { readFileSync } from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import * as XLSX from 'xlsx'
import { createTools } from '../../lib/plugin/tools.js'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..')
const readInput = (name) => readFileSync(path.join(root, 'samples', 'quickstart', 'input', name), 'utf8')
const sha = (value) => createHash('sha256').update(value).digest('hex')
const money = (cents) => (cents / 100).toFixed(2)

class MemoryTable {
  map = new Map()
  get(key) { return this.map.get(key) }
  entries() { return this.map.entries() }
  async put(key, value) { this.map.set(key, value) }
}

async function run() {
  const tripsCsv = readInput('trips.csv')
  const invoicesCsv = readInput('invoices.csv')
  const cardsCsv = readInput('cards.csv')

  const baseDir = await mkdtemp(path.join(os.tmpdir(), 'dsh-travel-quickstart-'))
  try {
    const tables = { trips: new MemoryTable(), invoices: new MemoryTable(), cards: new MemoryTable(), matches: new MemoryTable(), baseDir }
    const tools = Object.fromEntries(createTools(tables).map((tool) => [tool.name, tool]))
    const call = (name, args) => tools[name].execute(args, { callId: 'quickstart' })

    const ingest = await call('travel_ingest', {
      trips_csv: tripsCsv,
      invoices_csv: invoicesCsv,
      cards_csv: cardsCsv,
    })
    const match = await call('travel_match', {})
    const exported = await call('travel_export', {})
    const workbook = XLSX.read(await readFile(exported.path), { type: 'buffer' })
    const duplicates = await call('travel_duplicate_check', {})
    const policy = await call('travel_policy_check', { max_order_cents: 200000, require_invoice: true })
    const daily = await call('travel_daily_limit_check', { cap_cents: 300000 })
    const reuse = await call('travel_reuse_check', { invoices_csv: invoicesCsv, cards_csv: cardsCsv })

    const exceptions = [...tables.matches.entries()]
      .map(([, record]) => record)
      .filter((record) => record.state === 'exception')
      .map((record) => ({
        trip_id: record.trip_id,
        reason: record.reason,
        trip_delta_cents: record.trip_delta_cents,
        invoice_delta_cents: record.invoice_delta_cents,
      }))
      .sort((a, b) => a.trip_id.localeCompare(b.trip_id))

    const summary = {
      package: 'dsh-travel-recon',
      sample: 'synthetic/quickstart',
      ingest: {
        trips: ingest.trips,
        invoices: ingest.invoices,
        cards: ingest.cards,
        skipped: ingest.skipped,
        duplicate_trips: ingest.duplicate_trips,
      },
      match: { matched: match.matched, exceptions: match.exceptions, exception_detail: exceptions },
      duplicates: duplicates.duplicates
        .map((item) => ({ kind: item.kind, trip_id: item.trip_id, count: item.count }))
        .sort((a, b) => a.kind.localeCompare(b.kind) || a.trip_id.localeCompare(b.trip_id)),
      policy: {
        checked: policy.checked,
        violations: policy.violations
          .map((item) => ({ trip_id: item.trip_id, reason: item.reason }))
          .sort((a, b) => a.trip_id.localeCompare(b.trip_id)),
      },
      daily_limit: {
        days: daily.days,
        over_limit: daily.over_limit.map((item) => ({
          employee: item.employee,
          date: item.date,
          total_cents: item.total_cents,
          over_by_cents: item.over_by_cents,
        })),
      },
      reuse: {
        invoice_reuse: reuse.invoice_reuse,
        card_reuse: reuse.card_reuse,
      },
      workpaper: {
        sheets: workbook.SheetNames,
        rows: workbook.SheetNames.map((name) => XLSX.utils.sheet_to_json(workbook.Sheets[name], { header: 1 }).length),
      },
      input_sha256: {
        'trips.csv': sha(tripsCsv),
        'invoices.csv': sha(invoicesCsv),
        'cards.csv': sha(cardsCsv),
      },
    }

    if (process.argv.includes('--json')) {
      process.stdout.write(`${JSON.stringify(summary, null, 2)}\n`)
      return
    }

    const lines = [
      'dsh-travel-recon quickstart - synthetic sample, not customer data',
      `[1/5] ingest trip/invoice/card CSV ... trips=${ingest.trips} inv=${ingest.invoices} card=${ingest.cards}`,
      `[2/5] three-way match (±0.01) ....... matched=${match.matched} exceptions=${match.exceptions}`,
      `[3/5] export ledger ................ ${workbook.SheetNames.join('/')} sheets`,
      `[4/5] policy + daily limit .......... violations=${policy.violations.length} over-limit days=${daily.over_limit.length}`,
      `[5/5] duplicate / reuse check ....... duplicates=${duplicates.duplicates.length} reuse=${reuse.invoice_reuse.length + reuse.card_reuse.length}`,
      `result: matched=${match.matched} exceptions=${match.exceptions} trips=${ingest.trips}`,
      `exceptions: ${exceptions.map((item) => `${item.trip_id}:${item.reason}`).join(', ') || 'none'}`,
      `daily over: ${daily.over_limit.map((item) => `${item.date} +${money(item.over_by_cents)}`).join(', ') || 'none'}`,
      'quickstart ok',
    ]
    process.stdout.write(`${lines.join('\n')}\n`)
  } finally {
    await rm(baseDir, { recursive: true, force: true })
  }
}

await run()
