import path from'node:path';import type{Context}from'@deepseek-ai/cordis';import{createTools}from'./tools.js';import{openTravel}from'./storage.js'
export const name='dsh-travel-recon';export const inject=['tools','storageDomain']
export async function apply(ctx:Context):Promise<void>{const baseDir=process.env.DSH_TRAVEL_HOME??path.join(process.env.DSH_HOME??process.cwd(),'storages','dsh-travel-recon');const{trips,invoices,cards,matches}=await openTravel(ctx);for(const t of createTools({trips,invoices,cards,matches,baseDir}))ctx.tools.register(t)}
