import{mkdirSync,writeFileSync}from'node:fs';import{createHash}from'node:crypto';import{mkdtemp,rm,readFile}from'node:fs/promises';import os from'node:os';import path from'node:path';import * as XLSX from'xlsx';import{createTools}from'../lib/plugin/tools.js'
class T{map=new Map();get(k){return this.map.get(k)};entries(){return this.map.entries()};get size(){return this.map.size};async put(k,v){this.map.set(k,v)}}
const n=20,trips=['trip_id,employee,origin,destination,date,amount'],inv=['invoice_id,trip_id,amount'],cards=['txn_id,trip_id,amount'];for(let i=1;i<=n;i++){trips.push(`T${i},A,PEK,SHA,2026-01-01,100.00`);inv.push(`I${i},T${i},100.00`);cards.push(`C${i},T${i},100.00`)}
const d=await mkdtemp(path.join(os.tmpdir(),'travel-acc-'));const ts=createTools({trips:new T(),invoices:new T(),cards:new T(),matches:new T(),baseDir:path.join(d,'s')});const b=Object.fromEntries(ts.map(t=>[t.name,t]));const e={callId:'a'};const ing=await b['travel.ingest'].execute({trips_csv:trips.join('\n'),invoices_csv:inv.join('\n'),cards_csv:cards.join('\n')},e);const m=await b['travel.match'].execute({},e);const x=await b['travel.export'].execute({},e);const sheets=XLSX.read(await readFile(x.path),{type:'buffer'}).SheetNames.length;await rm(d,{recursive:true,force:true})
const dupTools=createTools({trips:new T(),invoices:new T(),cards:new T(),matches:new T(),baseDir:'/tmp/travel-dup'});const db=Object.fromEntries(dupTools.map(t=>[t.name,t]));await db['travel.ingest'].execute({trips_csv:'trip_id,employee,origin,destination,date,amount\nT1,A,PEK,SHA,2026-01-01,100.00',invoices_csv:'invoice_id,trip_id,amount\nI1,T1,100.00\nI2,T1,100.00',cards_csv:'txn_id,trip_id,amount\nC1,T1,100.00'},{callId:'a'});const dup=await db['travel.duplicate_check'].execute({},{callId:'a'});const ms=[{i:'SKU-15-A01',m:'行程解析',t:'20/20',a:ing.trips,p:ing.trips===20},{i:'SKU-15-A02',m:'三方匹配',t:'20/20',a:m.matched,p:m.matched===20},{i:'SKU-15-A03',m:'重复行程',t:'0',a:m.duplicate_trips,p:m.duplicate_trips===0},{i:'SKU-15-A04',m:'台账 sheet',t:'2',a:sheets,p:sheets===2},{i:'SKU-15-A05',m:'重复发票检测',t:'1',a:dup.duplicates.length,p:dup.duplicates.length===1}];const r={run_id:`sku15-${Date.now()}`,scope:'SKU-15-S1',status:'partial',counted:false,note:'synthetic trips/invoices/card; user-approved public/synthetic; 0 real firms',metrics:ms,pass:ms.every(x=>x.p)};const ev=`evidence/${r.run_id}`;mkdirSync(ev,{recursive:true});const s=JSON.stringify(r,null,2)+'\n';writeFileSync(`${ev}/result.json`,s);const h=createHash('sha256').update(s).digest('hex');writeFileSync('ACCEPTANCE.csv','req_id,metric,threshold,actual,script,evidence_sha256,pass\n'+ms.map(x=>`${x.i},${x.m},${x.t},${x.a},scripts/acceptance.mjs,${h},${x.p}`).join('\n')+'\n');if(!r.pass)process.exit(1);console.log('acceptance ok')


// Normalize the public-only acceptance schema: source + counted=false.
{
  const fs = await import('node:fs')
  const file = 'ACCEPTANCE.csv'
  const lines = fs.readFileSync(file, 'utf8').trim().split('\n')
  if (!lines[0].includes('source,counted')) {
    lines[0] += ',source,counted'
    for (let i = 1; i < lines.length; i += 1) lines[i] += ',public/synthetic,false'
    fs.writeFileSync(file, lines.join('\n') + '\n')
  }
}
