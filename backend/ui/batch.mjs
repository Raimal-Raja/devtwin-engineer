export const workflows=[
 ['repository-understanding','Repository understanding','Map structure, entry points and conventions.'],
 ['feature-tracing','Feature tracing','Follow behavior through the selected source.'],
 ['change-impact','Change impact','Review affected callers and contracts.'],
 ['bug-reproduction','Bug reproduction','Identify a focused reproduction and its blockers.'],
 ['dependency-diagnosis','Dependency diagnosis','Inspect dependencies and environment assumptions.'],
 ['implementation','Implementation','Plan a focused, evidence-based change.'],
 ['regression-testing','Regression testing','Identify meaningful regression checks.'],
 ['api-compatibility','API compatibility','Review interfaces and consumer expectations.'],
 ['database-review','Database review','Review schema, migration and data assumptions.'],
 ['security-review','Security review','Inspect concrete security-sensitive paths.'],
 ['performance-investigation','Performance investigation','Identify measurement and profiling opportunities.'],
 ['documentation-verification','Documentation verification','Compare documentation with supplied source.'],
 ['delivery-preparation','Delivery preparation','Prepare an evidence-based review checklist.']
].map(([id,name,description])=>({id,name,description}));

// One request per workflow, sequentially. Failures are evidence, never automatic retries.
export async function runBatch(ids,{execute,onProgress=()=>{},stopped=()=>false,pause=ms=>new Promise(r=>setTimeout(r,ms))}){
 if(!ids.length||ids.length>13||new Set(ids).size!==ids.length||ids.some(id=>!workflows.some(w=>w.id===id)))throw new Error('Select valid unique workflows');
 const results=[];
 for(const id of ids){
  if(stopped())break;
  if(results.length){onProgress({id,status:'waiting',completed:results.length,total:ids.length});await pause(15000);if(stopped())break;}
  onProgress({id,status:'running',completed:results.length,total:ids.length});
  let item;
  try{const report=await execute(id);item={id,status:'completed',report};}
  catch(error){item={id,status:'failed',error:error.message||'Investigation failed'};}
  results.push(item);onProgress({...item,completed:results.length,total:ids.length});
 }
 return {status:stopped()?'stopped':results.some(r=>r.status==='failed')?'completed_with_errors':'completed',
  results,requested:ids.length,completed:results.length,applied_changes:[],executed_commands:[],
  limitations:['Source investigations only; tests and changes require separate reviewed actions.','Results depend on the selected files and provider availability.']};
}
