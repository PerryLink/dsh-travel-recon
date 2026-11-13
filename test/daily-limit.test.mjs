import test from 'node:test'
import assert from 'node:assert/strict'
import { createTools } from '../lib/plugin/tools.js'

class T { map = new Map(); get(k){return this.map.get(k)}; entries(){return this.map.entries()}; get size(){return this.map.size}; async put(k,v){this.map.set(k,v)} }
const setup = async () => {
  const tools = createTools({ trips: new T(), invoices: new T(), cards: new T(), matches: new T(), baseDir: '/tmp/travel-daily' })
  const by = Object.fromEntries(tools.map((t) => [t.name, t]))
  await by['travel_ingest'].execute({
    trips_csv: 'trip_id,employee,origin,destination,date,amount\nT1,A,PEK,SHA,2026-02-01,60.00\nT2,A,PEK,SHA,2026-02-01,50.00\nT3,B,PEK,SHA,2026-02-01,20.00\nT4,A,PEK,SHA,2026-02-02,10.00',
    invoices_csv: 'invoice_id,trip_id,amount\nI1,T1,60.00\nI2,T2,50.00\nI3,T3,20.00\nI4,T4,10.00',
    cards_csv: 'txn_id,trip_id,amount\nC1,T1,60.00\nC2,T2,50.00\nC3,T3,20.00\nC4,T4,10.00',
  }, { callId: 'd' })
  return by
}

test('a day over the cap is reported with the overage', async () => {
  const by = await setup()
  const r = await by['travel_daily_limit_check'].execute({ cap_cents: 10000 }, { callId: 'd' })
  assert.equal(r.days, 3)
  assert.equal(r.over_limit.length, 1)
  assert.equal(r.over_limit[0].employee, 'A')
  assert.equal(r.over_limit[0].date, '2026-02-01')
  assert.equal(r.over_limit[0].total_cents, 11000)
  assert.equal(r.over_limit[0].over_by_cents, 1000)
})

test('a generous cap reports nothing and the day count stays right', async () => {
  const by = await setup()
  const r = await by['travel_daily_limit_check'].execute({ cap_cents: 100000 }, { callId: 'd' })
  assert.equal(r.days, 3)
  assert.deepEqual(r.over_limit, [])
})
