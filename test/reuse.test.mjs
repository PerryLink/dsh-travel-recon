import test from 'node:test'
import assert from 'node:assert/strict'
import { createTools } from '../lib/plugin/tools.js'

class T { map = new Map(); get(k){return this.map.get(k)}; entries(){return this.map.entries()}; get size(){return this.map.size}; async put(k,v){this.map.set(k,v)} }
const tools = Object.fromEntries(createTools({ trips: new T(), invoices: new T(), cards: new T(), matches: new T(), baseDir: '/tmp/travel-reuse' }).map((t) => [t.name, t]))
const exec = { callId: 'reuse' }

test('an invoice re-used on two trips is reported before ingest', async () => {
  const r = await tools['travel_reuse_check'].execute({
    invoices_csv: 'invoice_id,trip_id,amount\nI1,T1,100.00\nI1,T2,100.00\nI2,T1,50.00',
    cards_csv: 'txn_id,trip_id,amount\nC1,T1,100.00',
  }, exec)
  assert.equal(r.invoice_reuse.length, 1)
  assert.equal(r.invoice_reuse[0].id, 'I1')
  assert.deepEqual(r.invoice_reuse[0].trips, ['T1', 'T2'])
  assert.equal(r.card_reuse.length, 0)
})

test('a card transaction re-used on two trips is reported', async () => {
  const r = await tools['travel_reuse_check'].execute({
    invoices_csv: 'invoice_id,trip_id,amount\nI1,T1,100.00',
    cards_csv: 'txn_id,trip_id,amount\nC9,T1,20.00\nC9,T3,20.00',
  }, exec)
  assert.equal(r.card_reuse.length, 1)
  assert.equal(r.card_reuse[0].id, 'C9')
  assert.deepEqual(r.card_reuse[0].trips, ['T1', 'T3'])
})

test('clean statements report no reuse', async () => {
  const r = await tools['travel_reuse_check'].execute({
    invoices_csv: 'invoice_id,trip_id,amount\nI1,T1,100.00\nI2,T2,90.00',
    cards_csv: 'txn_id,trip_id,amount\nC1,T1,100.00\nC2,T2,90.00',
  }, exec)
  assert.equal(r.invoice_reuse.length, 0)
  assert.equal(r.card_reuse.length, 0)
})
