import test from 'node:test';
import assert from 'node:assert/strict';
import {runBatch,workflows} from '../backend/ui/batch.mjs';

test('all thirteen investigations run once and sequentially with preserved failure evidence',async()=>{
 const calls=[],pauses=[],events=[];let active=0;
 const result=await runBatch(workflows.map(w=>w.id),{pause:async ms=>pauses.push(ms),onProgress:e=>events.push(e),execute:async id=>{
  assert.equal(active,0);active++;await Promise.resolve();calls.push(id);active--;
  if(id==='security-review')throw new Error('Provider unavailable');return {workflow:id,status:'unverified_source_analysis'};
 }});
 assert.equal(calls.length,13);assert.equal(new Set(calls).size,13);assert.equal(pauses.length,12);
 assert.ok(pauses.every(ms=>ms===15000));assert.equal(result.status,'completed_with_errors');
 assert.equal(result.results.find(r=>r.id==='security-review').error,'Provider unavailable');
 assert.equal(result.results.filter(r=>r.status==='completed').length,12);
 assert.deepEqual(result.applied_changes,[]);assert.deepEqual(result.executed_commands,[]);
 assert.equal(events.filter(e=>e.status==='running').length,13);
});
test('stopping preserves the current result and makes no further provider calls',async()=>{
 let stop=false,calls=0;
 const result=await runBatch(workflows.map(w=>w.id),{stopped:()=>stop,pause:async()=>{},execute:async()=>{calls++;stop=true;return {summary:'first'};}});
 assert.equal(result.status,'stopped');assert.equal(calls,1);assert.equal(result.completed,1);
});
test('stop during quota pacing cancels the next submission',async()=>{
 let stop=false,calls=0;
 const result=await runBatch(workflows.map(w=>w.id),{stopped:()=>stop,pause:async()=>{stop=true;},execute:async()=>{calls++;return {};}});
 assert.equal(result.status,'stopped');assert.equal(calls,1);
});
test('empty, unknown or duplicate workflow selections cannot submit',async()=>{
 for(const ids of [[],['unknown'],['implementation','implementation']])await assert.rejects(runBatch(ids,{execute:()=>assert.fail('Must not submit')}));
});
