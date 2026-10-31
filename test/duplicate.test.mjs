import test from 'node:test'
import assert from 'node:assert/strict'
import { createTools } from '../lib/plugin/tools.js'
class T { map=new Map(); get(k){return this.map.get(k)}; entries(){return this.map.entries()}; get size(){return this.map.size}; async put(k,v){this.map.set(k,v)} }
test('duplicate invoice for same trip', async () => {
  const tools = createTools({ trips: new T(), invoices: new T(), cards: new T(), matches: new T(), baseDir: '/tmp/travel-dup' })
  const by = Object.fromEntries(tools.map((tool) => [tool.name, tool]))
  await by['travel.ingest'].execute({ trips_csv: 'trip_id,employee,origin,destination,date,amount\nT1,A,PEK,SHA,2026-01-01,100.00', invoices_csv: 'invoice_id,trip_id,amount\nI1,T1,100.00\nI2,T1,100.00', cards_csv: 'txn_id,trip_id,amount\nC1,T1,100.00' }, { callId: 'd' })
  const result = await by['travel.duplicate_check'].execute({}, { callId: 'd' })
  assert.equal(result.duplicates.length, 1)
  assert.equal(result.duplicates[0].kind, 'invoice')
})
