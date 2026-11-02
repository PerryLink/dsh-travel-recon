import test from 'node:test'
import assert from 'node:assert/strict'
import { mkdtemp, rm } from 'node:fs/promises'
import os from 'node:os'
import path from 'node:path'
import { createTools } from '../lib/plugin/tools.js'

class T { map = new Map(); get(k) { return this.map.get(k) }; entries() { return this.map.entries() }; get size() { return this.map.size }; async put(k, v) { this.map.set(k, v) } }

const trips = 'trip_id,employee,origin,destination,date,amount\nT1,A,PEK,SHA,2026-01-01,100.00\nT2,A,PEK,SHA,2026-01-02,50.00'
const invoices = 'invoice_id,trip_id,amount\nI1,T1,100.00\nI2,T2,50.00'
const cards = 'txn_id,trip_id,amount\nC1,T1,100.00\nC2,T2,50.00'

test('re-ingesting the same CSV set is idempotent and reports skipped rows', async () => {
  const dir = await mkdtemp(path.join(os.tmpdir(), 'dsh-travel-idem-'))
  try {
    const tables = { trips: new T(), invoices: new T(), cards: new T(), matches: new T() }
    const tools = createTools({ ...tables, baseDir: path.join(dir, 'store') })
    const by = Object.fromEntries(tools.map((tool) => [tool.name, tool]))
    const exec = { callId: 'idem' }
    const first = await by['travel.ingest'].execute({ trips_csv: trips, invoices_csv: invoices, cards_csv: cards }, exec)
    assert.equal(first.skipped, 0)
    assert.equal(tables.trips.size, 2)
    assert.equal(tables.invoices.size, 2)
    assert.equal(tables.cards.size, 2)
    const second = await by['travel.ingest'].execute({ trips_csv: trips, invoices_csv: invoices, cards_csv: cards }, exec)
    assert.equal(second.skipped, 6)
    assert.equal(tables.trips.size, 2)
    assert.equal(tables.invoices.size, 2)
    assert.equal(tables.cards.size, 2)
  } finally { await rm(dir, { recursive: true, force: true }) }
})
