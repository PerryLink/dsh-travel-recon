import test from 'node:test'
import assert from 'node:assert/strict'
import { mkdtemp, rm } from 'node:fs/promises'
import os from 'node:os'
import path from 'node:path'
import { duplicateTrips, parseTrips } from '../lib/core/travel.js'
import { createTools } from '../lib/plugin/tools.js'

class T { map = new Map(); get(k) { return this.map.get(k) }; entries() { return this.map.entries() }; get size() { return this.map.size }; async put(k, v) { this.map.set(k, v) } }

const dupTrips = 'trip_id,employee,origin,destination,date,amount\nT1,A,PEK,SHA,2026-01-01,100.00\nT1,A,PEK,SHA,2026-01-01,100.00\nT2,B,PEK,SHA,2026-01-02,50.00'
const invoices = 'invoice_id,trip_id,amount\nI1,T1,100.00\nI2,T2,50.00'
const cards = 'txn_id,trip_id,amount\nC1,T1,100.00\nC2,T2,50.00'

test('duplicate trip ids are detected on the parsed CSV rows', () => {
  const dups = duplicateTrips(parseTrips(dupTrips))
  assert.deepEqual(dups, [{ trip_id: 'T1', occurrences: 2 }])
})

test('ingest retains duplicate trip rows and reports them as issues instead of overwriting', async () => {
  const dir = await mkdtemp(path.join(os.tmpdir(), 'dsh-travel-dup-'))
  try {
    const tables = { trips: new T(), invoices: new T(), cards: new T(), matches: new T() }
    const tools = createTools({ ...tables, baseDir: path.join(dir, 'store') })
    const by = Object.fromEntries(tools.map((tool) => [tool.name, tool]))
    const result = await by['travel.ingest'].execute({ trips_csv: dupTrips, invoices_csv: invoices, cards_csv: cards }, { callId: 'dup' })
    assert.equal(result.trips, 3)
    assert.equal(result.duplicate_trips, 1)
    assert.equal(result.issues.length, 1)
    assert.equal(result.issues[0].code, 'E_TRAVEL_TRIP_DUPLICATE')
    assert.equal(result.issues[0].trip_id, 'T1')
    assert.equal(result.issues[0].occurrences, 2)
    // Both CSV rows are kept: the later trip_id no longer overwrites the earlier one.
    assert.equal(tables.trips.size, 3)
    assert.equal([...tables.trips.entries()].filter(([, trip]) => trip.trip_id === 'T1').length, 2)
  } finally { await rm(dir, { recursive: true, force: true }) }
})

test('match counts the duplicate trip and matches the unique trips only', async () => {
  const dir = await mkdtemp(path.join(os.tmpdir(), 'dsh-travel-dup-'))
  try {
    const tools = createTools({ trips: new T(), invoices: new T(), cards: new T(), matches: new T(), baseDir: path.join(dir, 'store') })
    const by = Object.fromEntries(tools.map((tool) => [tool.name, tool]))
    const exec = { callId: 'dup' }
    await by['travel.ingest'].execute({ trips_csv: dupTrips, invoices_csv: invoices, cards_csv: cards }, exec)
    const result = await by['travel.match'].execute({}, exec)
    assert.equal(result.duplicate_trips, 1)
    assert.equal(result.matched, 2)
    assert.equal(result.exceptions, 0)
  } finally { await rm(dir, { recursive: true, force: true }) }
})
