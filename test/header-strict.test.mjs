import test from 'node:test'
import assert from 'node:assert/strict'
import { parseCards, parseInvoices, parseTrips } from '../lib/core/travel.js'

test('a missing trip header column is an error, not an empty id', () => {
  assert.throws(() => parseTrips('trip_id,employee,origin,destination,date\nT1,A,X,Y,2026-01-01'), /E_TRAVEL_CSV_INVALID/)
  assert.throws(() => parseTrips('T1,A,X,Y,2026-01-01,100.00\nT2,B,X,Y,2026-01-02,50.00'), /E_TRAVEL_CSV_INVALID/)
})

test('a missing invoice header column is an error, not an empty trip_id', () => {
  assert.throws(() => parseInvoices('invoice_id,amount\nI1,100.00'), /E_TRAVEL_CSV_INVALID/)
  assert.throws(() => parseInvoices('I1,T1,100.00\nI2,T2,50.00'), /E_TRAVEL_CSV_INVALID/)
})

test('a missing card header column is an error, not an empty trip_id', () => {
  assert.throws(() => parseCards('txn_id,amount\nC1,100.00'), /E_TRAVEL_CSV_INVALID/)
  assert.throws(() => parseCards('C1,T1,100.00\nC2,T2,50.00'), /E_TRAVEL_CSV_INVALID/)
})

test('empty primary keys are rejected', () => {
  assert.throws(() => parseTrips('trip_id,employee,origin,destination,date,amount\n,A,X,Y,2026-01-01,100.00'), /E_TRAVEL_CSV_INVALID/)
  assert.throws(() => parseInvoices('invoice_id,trip_id,amount\n,T1,100.00'), /E_TRAVEL_CSV_INVALID/)
  assert.throws(() => parseCards('txn_id,trip_id,amount\n,T1,100.00'), /E_TRAVEL_CSV_INVALID/)
})
