import test from 'node:test'
import assert from 'node:assert/strict'
import { createTools } from '../lib/plugin/tools.js'

class T { map=new Map(); get(k){return this.map.get(k)}; entries(){return this.map.entries()}; get size(){return this.map.size}; async put(k,v){this.map.set(k,v)} }

test('travel policy check over/missing invoice', async () => {
  const trips = new T(); const invoices = new T(); const cards = new T(); const matches = new T()
  await trips.put('t1', { trip_id:'t1', traveler:'A', amount_cents:120000, created_at:'' })
  await trips.put('t2', { trip_id:'t2', traveler:'B', amount_cents:50000, created_at:'' })
  await invoices.put('i1', { invoice_id:'i1', trip_id:'t1', amount_cents:120000, created_at:'' })
  const tools = createTools({ trips, invoices, cards, matches, baseDir: '/tmp/travel-policy' })
  const check = tools.find((tool) => tool.name === 'travel.policy_check')
  const result = await check.execute({ max_order_cents: 100000, require_invoice: true }, { callId: 'policy' })
  assert.equal(result.checked, 2)
  assert.ok(result.violations.some((v) => v.trip_id === 't1' && v.reason === 'over_policy'))
  assert.ok(result.violations.some((v) => v.trip_id === 't2' && v.reason === 'missing_invoice'))
})
