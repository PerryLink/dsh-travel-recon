export type TravelErrorCode='E_TRAVEL_CSV_INVALID'|'E_TRAVEL_TRIP_MISSING'|'E_TRAVEL_TRIP_DUPLICATE'|'E_TRAVEL_MATCH_FAILED'|'E_TRAVEL_EXPORT_FAILED'|'E_TRAVEL_PATH_INVALID'|'E_TRAVEL_PATH_NOT_ALLOWED'
export class TravelError extends Error{readonly code:TravelErrorCode;constructor(code:TravelErrorCode,message:string,next?:string){super(next?`${message}（${code}）｜下一步：${next}`:`${message}（${code}）`);this.name='TravelError';this.code=code}}
export interface Trip{trip_id:string;employee:string;origin:string;destination:string;date:string;amount_cents:number}
export interface Invoice{invoice_id:string;trip_id:string;amount_cents:number}
export interface Card{txn_id:string;trip_id:string;amount_cents:number}
export interface Match{match_id:string;trip_id:string;invoice_id?:string;card_id?:string;order_cents:number;invoice_cents:number;card_cents:number;trip_delta_cents:number;invoice_delta_cents:number;state:'matched'|'exception';reason:string;created_at:string}
export function cents(raw:string):number{const v=raw.trim().replace(/[¥￥,\s]/g,'');const m=/^(-?)(\d+)(?:\.(\d{1,2}))?$/.exec(v);if(!m)throw new TravelError('E_TRAVEL_CSV_INVALID',`金额“${raw}”读不懂`,'把金额改成 1234.56 这样的纯数字，最多两位小数');return (m[1]==='-'?-1:1)*(Number(m[2])*100+Number((m[3]??'').padEnd(2,'0')))}
function rows(t:string){const l=t.trim().split(/\r?\n/).filter(Boolean);if(l.length<2)throw new TravelError('E_TRAVEL_CSV_INVALID','CSV needs header+rows');return l.map(x=>x.split(',').map(y=>y.trim()))}
function headerIndex(h:string[],n:string):number{const i=h.indexOf(n);if(i<0)throw new TravelError('E_TRAVEL_CSV_INVALID',`CSV 缺少 ${n} 列`,'按 README 的列名补齐第一行表头后重跑');return i}
export function parseTrips(t:string):Trip[]{
  const r=rows(t);const h=r[0]!.map(x=>x.toLowerCase())
  const ti=headerIndex(h,'trip_id'),ei=headerIndex(h,'employee'),oi=headerIndex(h,'origin'),di=headerIndex(h,'destination'),dti=headerIndex(h,'date'),ai=headerIndex(h,'amount')
  return r.slice(1).map(c=>{const trip:Trip={trip_id:c[ti]??'',employee:c[ei]??'',origin:c[oi]??'',destination:c[di]??'',date:c[dti]??'',amount_cents:cents(c[ai]??'')};if(!trip.trip_id)throw new TravelError('E_TRAVEL_CSV_INVALID','行程行缺少 trip_id','给每一行填上唯一 trip_id（如 TRIP-1001）后重跑');return trip})
}
export function parseInvoices(t:string):Invoice[]{
  const r=rows(t);const h=r[0]!.map(x=>x.toLowerCase())
  const ii=headerIndex(h,'invoice_id'),ti=headerIndex(h,'trip_id'),ai=headerIndex(h,'amount')
  return r.slice(1).map(c=>{const invoice:Invoice={invoice_id:c[ii]??'',trip_id:c[ti]??'',amount_cents:cents(c[ai]??'')};if(!invoice.invoice_id)throw new TravelError('E_TRAVEL_CSV_INVALID','empty invoice_id');return invoice})
}
export function parseCards(t:string):Card[]{
  const r=rows(t);const h=r[0]!.map(x=>x.toLowerCase())
  const ti=headerIndex(h,'txn_id'),tri=headerIndex(h,'trip_id'),ai=headerIndex(h,'amount')
  return r.slice(1).map(c=>{const card:Card={txn_id:c[ti]??'',trip_id:c[tri]??'',amount_cents:cents(c[ai]??'')};if(!card.txn_id)throw new TravelError('E_TRAVEL_CSV_INVALID','empty txn_id');return card})
}
export interface DuplicateTrip{trip_id:string;occurrences:number}
/** Duplicate trip ids in the raw CSV rows; the first occurrence is kept, the rest are reported. */
export function duplicateTrips(trips:Trip[]):DuplicateTrip[]{
  const counts=new Map<string,number>()
  for(const trip of trips)counts.set(trip.trip_id,(counts.get(trip.trip_id)??0)+1)
  return [...counts.entries()].filter(([,occurrences])=>occurrences>1).map(([trip_id,occurrences])=>({trip_id,occurrences}))
}
