import {sessionToken,githubInput} from '/github.mjs'; import {runBatch,workflows as allWorkflows} from '/batch.mjs';
const $=id=>document.getElementById(id);
let githubSnapshot=null;
let batchReport=null,batchStop=false;
function emit(name,detail){document.dispatchEvent?.(new CustomEvent(name,{detail}));}
function resetBatch(){emit('batch-reset');batchReport=null;$('download-all').disabled=true;$('approve-batch').checked=false;$('batch-progress').value=0;$('batch-status').textContent='Preview files and approve provider submission to begin.';}
let archive='',previewSignature='',report=null,provider='',proposal=null,publicInputRequired=false;
let runnableSelection=false;
const selection=()=>$('selected').value.split(/\r?\n/).map(x=>x.trim()).filter(Boolean);
const signature=()=>JSON.stringify([archive,selection()]);
function clearPatch(){proposal=null;$('patch').textContent='No current patch.';$('approve-patch').checked=false;$('approve-run').checked=false;$('verification').textContent='No checks executed.';for(const id of ['approve-patch','download-patch','approve-run','verify'])$(id).disabled=true;}
function clearResults(){resetBatch();report=null;clearPatch();$('result').textContent='No current report.';$('repair-result').textContent='No repair loop executed.';$('export').disabled=true;$('approve-loop').checked=false;}
function invalidate(){resetBatch();runnableSelection=false;emit('selection-invalidated');previewSignature='';provider='';publicInputRequired=false;report=null;clearPatch();$('approve-loop').checked=false;$('repair-result').textContent='No repair loop executed.';$('consent').checked=false;$('investigate').disabled=true;$('propose').disabled=true;$('repair').disabled=true;$('export').disabled=true;$('files').textContent='Selection changed. Preview files again.';$('result').textContent='No current report.';}
function lockInputs(busy){for(const id of ['token','archive','selected','task','workflow','consent','repository','ref','github','github-browse','approve-loop'])$(id).disabled=busy;for(const item of $('github-list').querySelectorAll('input'))item.disabled=busy;for(const id of ['preview','investigate','propose','repair'])$(id).disabled=busy||((id!=='preview')&&!previewSignature);for(const id of ['approve-patch','download-patch','approve-run','verify'])$(id).disabled=busy||!proposal;$('workflow').disabled=busy||!previewSignature;$('repair').disabled=busy||!previewSignature||!runnableSelection;$('verify').disabled=busy||!proposal||!runnableSelection;$('run-all').disabled=busy||!previewSignature;$('approve-batch').disabled=busy;}
async function request(route,data){
  const response=await fetch(route,{method:'POST',headers:{'Content-Type':'application/json','Authorization':'Bearer '+sessionToken($('token').value)},body:JSON.stringify(data),cache:'no-store'});
  const result=await response.json();
  if(!response.ok)throw new Error(result.error||'Request failed');
  return result;
}
$('archive').addEventListener('change',async()=>{
  $('github-source').textContent='Using an uploaded ZIP.';
  archive='';invalidate();const file=$('archive').files[0];if(!file)return;
  if(file.size>2*1024*1024){$('status').textContent='ZIP exceeds 2 MiB.';return;}
  try{const bytes=new Uint8Array(await file.arrayBuffer());let raw='';for(const byte of bytes)raw+=String.fromCharCode(byte);archive=btoa(raw);$('status').textContent='ZIP loaded locally. Select exact file paths and preview.';}catch{$('status').textContent='ZIP could not be loaded.';}
});
$('selected').addEventListener('input',invalidate);
for(const id of ['repository','ref'])$(id).addEventListener('input',()=>{githubSnapshot=null;$('github-list').textContent='Browse this repository to choose files.';});
$('github-browse').addEventListener('click',async()=>{
  try{sessionToken($('token').value);githubInput($('repository').value,$('ref').value,[],false);}catch(error){$('github-source').textContent=error.message;return;}
  lockInputs(true);$('github-source').textContent='Reading repository file list; no source submission to a model…';
  try{const result=await request('/api/github/tree',githubInput($('repository').value,$('ref').value,[],false));
    githubSnapshot={input:JSON.stringify([$('repository').value.trim(),$('ref').value.trim()]),commit:result.commit};
    $('github-list').replaceChildren();
    for(const file of result.files){const label=document.createElement('label'),input=document.createElement('input');label.className='consent';input.type='checkbox';input.value=file.path;input.checked=selection().includes(file.path);label.append(input,document.createTextNode(`${file.path} · ${file.bytes} bytes`));input.addEventListener('change',()=>{$('selected').value=[...$('github-list').querySelectorAll('input:checked')].map(item=>item.value).join('\n');invalidate();});$('github-list').append(label);}
    if(!result.files.length)$('github-list').textContent='No supported text files within the current size limit.';
    $('github-source').textContent=`${result.repository} · ${result.ref} · ${result.commit} · choose files, then import. ${result.files_truncated?'Showing the first 250 eligible files. ':''}Content is validated during import. ${result.omitted?`Omitted: ${result.omitted.oversize} files exceed the 16,000-byte limit; ${result.omitted.unsupported_or_excluded} unsupported/excluded files. Not all repository files are listed.`:''} ${(result.oversize_files||[]).map(file=>`${file.path} (${file.bytes} bytes) exceeds the selection limit.`).join(' ')}`;
  }catch(error){githubSnapshot=null;$('github-list').textContent='No file list loaded.';$('github-source').textContent=`GitHub browse failed: ${error.message}`;}finally{lockInputs(false);}
});
$('github').addEventListener('click',async()=>{
  let input;try{sessionToken($('token').value);input=githubInput($('repository').value,$('ref').value,selection());}catch(error){$('github-source').textContent=error.message;return;}
  if(githubSnapshot?.input===JSON.stringify([input.repository,input.ref]))input.ref=githubSnapshot.commit;
  archive='';invalidate();lockInputs(true);$('status').textContent='Importing selected GitHub files; no model call…';$('github-source').textContent='Import pending.';
  try{const result=await request('/api/github',input);
    archive=result.archive;$('archive').value='';$('github-source').textContent=`${result.repository} · ${result.commit} · ${result.private?'Private':'Public'} · read-only import. No model submission.`;
    $('status').textContent='GitHub import ready. Preview selected files before provider submission.';
  }catch(error){$('github-source').textContent=`GitHub import failed: ${error.message}`;$('status').textContent=error.message;}finally{lockInputs(false);$('workflow').disabled=true;}
});
$('preview').addEventListener('click',async()=>{
  invalidate();lockInputs(true);$('preview').disabled=true;$('status').textContent='Validating selection…';
  try{const current=signature();const result=await request('/api/preview',{archive,selected:selection()});if(current!==signature())throw new Error('Selection changed; preview again.');
    $('files').textContent=result.files.map(file=>`${file.path}\nSHA-256: ${file.sha256}\n${file.content}`).join('\n\n');
    $('workflow').replaceChildren(...result.workflows.map(value=>{const option=document.createElement('option');option.value=value;option.textContent=value.replaceAll('-',' ');return option;}));
    provider=result.provider.id;publicInputRequired=result.provider.public_input_required===true;$('provider-details').textContent=`${result.provider.name} · ${result.provider.model}. ${result.provider.notice} ${result.provider.configured?'':'API key is not configured.'}`;
    $('provider-consent').textContent=(publicInputRequired?'I confirm these files and my task are public or synthetic, and approve upstream storage/training. ':'')+`I approve sending these selected, nonconfidential files and my task to ${result.provider.name} under the policy shown above.`;
    emit('preview-ready',result);
    runnableSelection=result.files.some(file=>/(^|\/)test[^/]*\.py$/.test(file.path));
    $('runner-readiness').textContent=runnableSelection?'Selected Python test modules found. Actual discovery, dependencies and results are checked only inside Docker.':'No Python test modules selected. Investigation and proposals are available; isolated verification and repair need test*.py unittest files and their source dependencies. Documentation alone cannot verify an application.';
    $('workflow').disabled=false;previewSignature=current;$('investigate').disabled=false;$('propose').disabled=false;$('status').textContent='Preview ready. Nothing has been sent to the model.';
  }catch(error){$('status').textContent=error.message;}finally{lockInputs(false);$('workflow').disabled=!previewSignature;$('preview').disabled=false;}
});
$('investigate').addEventListener('click',async()=>{
  if(previewSignature!==signature()||!$('consent').checked){$('status').textContent='Preview current files and approve submission first.';return;}
  const current=signature();clearResults();lockInputs(true);$('preview').disabled=true;$('investigate').disabled=true;$('status').textContent='Investigating source; no commands or tests are running…';
  try{const result=await request('/api/investigate',{archive,selected:selection(),task:$('task').value,workflow:$('workflow').value,consent:true,public_input_confirmed:publicInputRequired,provider});
    if(current!==signature())throw new Error('Selection changed; discard this response and investigate again.');
    report=result;$('result').textContent=JSON.stringify(result,null,2);$('export').disabled=false;$('status').textContent='Source analysis ready. Findings and proposed checks remain unverified.';
  }catch(error){$('result').textContent='No successful report.';$('status').textContent=error.message;}finally{lockInputs(false);$('preview').disabled=false;$('investigate').disabled=previewSignature!==signature();}
});
$('export').addEventListener('click',()=>{if(!report)return;const url=URL.createObjectURL(new Blob([JSON.stringify(report,null,2)],{type:'application/json'}));const link=document.createElement('a');link.href=url;link.download='devtwin-investigation.json';link.click();URL.revokeObjectURL(url);});
for(const [id,event] of [['task','input'],['workflow','change']])$(id).addEventListener(event,()=>{clearResults();$('consent').checked=false;$('status').textContent='Task or workflow changed. Review and approve submission again.';});
$('propose').addEventListener('click',async()=>{
  if(previewSignature!==signature()||!$('consent').checked){$('status').textContent='Preview current files and approve provider submission first.';return;}
  clearPatch();lockInputs(true);$('status').textContent='Proposing a change; no tests or edits are running…';
  try{proposal=await request('/api/propose',{archive,selected:selection(),task:$('task').value,consent:true,public_input_confirmed:publicInputRequired,provider});
    $('patch').textContent=`${proposal.explanation}\n\n${proposal.diff}\n\nComplete replacement for ${proposal.patch.path}:\n${proposal.patch.replacement}`;
    $('approve-patch').disabled=false;$('download-patch').disabled=false;$('status').textContent='Patch proposed. Review before approval; correctness is unverified.';
  }catch(error){clearPatch();$('status').textContent=error.message;}finally{lockInputs(false);}
});
$('download-patch').addEventListener('click',async()=>{
  if(!proposal||!$('approve-patch').checked){$('status').textContent='Review and approve this patch before export.';return;}
  lockInputs(true);$('download-patch').disabled=true;$('approve-patch').disabled=true;
  try{const result=await request('/api/export',{archive,selected:selection(),patch:proposal.patch,approved:true});
    const bytes=Uint8Array.from(atob(result.archive),char=>char.charCodeAt(0));const url=URL.createObjectURL(new Blob([bytes],{type:'application/zip'}));
    const link=document.createElement('a');link.href=url;link.download='devtwin-selected-candidate.zip';link.click();URL.revokeObjectURL(url);
    $('status').textContent='Selected-file candidate exported. Export performed no additional tests; the original upload is unchanged.';
  }catch(error){$('status').textContent=error.message;}finally{lockInputs(false);$('download-patch').disabled=!proposal;$('approve-patch').disabled=!proposal;}
});
$('verify').addEventListener('click',async()=>{
  if(!runnableSelection){$('status').textContent='Select Python unittest files (test*.py) and their source dependencies, then import and preview again.';return;}
  if(!proposal||!$('approve-patch').checked||!$('approve-run').checked){$('status').textContent='Approve the reviewed patch and isolated execution before running checks.';return;}
  lockInputs(true);$('status').textContent='Running original and candidate isolated checks…';$('verification').textContent='Verification pending.';
  try{const result=await request('/api/verify',{archive,selected:selection(),patch:proposal.patch,approved:true,execution_approved:true});
    $('verification').textContent=JSON.stringify(result,null,2);$('status').textContent=`Verification ${result.status}. Review actual scope and limitations.`;
  }catch(error){$('verification').textContent='No successful verification report.';$('status').textContent=error.message;}finally{lockInputs(false);}
});
$('repair').addEventListener('click',async()=>{
  if(!runnableSelection){$('status').textContent='Repair needs selected Python unittest files (test*.py) and their source dependencies. Documentation-only selections support investigation.';return;}
  if(previewSignature!==signature()||!$('consent').checked||!$('approve-loop').checked){$('status').textContent='Preview files and approve provider submission and the bounded repair loop first.';return;}
  clearResults();lockInputs(true);$('export').disabled=true;$('status').textContent='Running bounded investigation, candidate generation and isolated checks…';$('repair-result').textContent='Repair pending.';
  try{const result=await request('/api/repair',{archive,selected:selection(),task:$('task').value,workflow:$('workflow').value,consent:true,public_input_confirmed:publicInputRequired,provider,loop_approved:true});
    report=result;$('repair-result').textContent=JSON.stringify(result,null,2);$('export').disabled=false;
    $('result').textContent=result.analysis?JSON.stringify(result.analysis,null,2):'No investigation completed. See the repair outcome for the failed stage and recovery guidance.';
    const last=result.attempts?.at(-1);
    if(last&&result.patch){proposal=last.proposal;$('patch').textContent=`${proposal.explanation}\n\n${proposal.diff}\n\nComplete replacement for ${proposal.patch.path}:\n${proposal.patch.replacement}`;$('verification').textContent=JSON.stringify(last.verification,null,2);}
    $('status').textContent=`${result.reason || `Repair ${result.status}.`} Review the evidence and final replacement before export.`;
  }catch(error){$('repair-result').textContent='No successful repair report.';$('status').textContent=error.message;}finally{lockInputs(false);}
});

$('stop-all').addEventListener('click',()=>{batchStop=true;$('stop-all').disabled=true;$('batch-status').textContent='Stopping after the current request or pacing interval. Completed results will remain available.';});
$('run-all').addEventListener('click',async()=>{
  if(previewSignature!==signature()||!$('consent').checked||!$('approve-batch').checked){$('batch-status').textContent='Preview current files and approve provider submission plus the 13-request run first.';return;}
  if(!$('task').value.trim()||new TextEncoder().encode($('task').value).length>2000){$('batch-status').textContent='Enter a task of 1 to 2,000 UTF-8 bytes before starting.';return;}
  try{sessionToken($('token').value);}catch(error){$('batch-status').textContent=error.message;return;}
  const payload={archive,selected:selection(),task:$('task').value,provider,consent:true,public_input_confirmed:publicInputRequired};
  clearResults();batchStop=false;lockInputs(true);$('stop-all').disabled=false;
  try{
    batchReport=await runBatch(allWorkflows.map(w=>w.id),{
      stopped:()=>batchStop,
      execute:workflow=>request('/api/investigate',{...payload,workflow}),
      onProgress:item=>{emit('batch-progress',item);$('batch-status').textContent=`${item.completed}/13 completed · ${item.id.replaceAll('-',' ')} · ${item.status}${item.status==='waiting'?' (pacing requests for quotas)':''}`;}
    });
    $('batch-status').textContent=`${batchReport.status.replaceAll('_',' ')} · ${batchReport.completed}/13 processed · ${batchReport.results.filter(r=>r.status==='failed').length} failed. Review each report; no tests ran or changes were applied.`;
    $('download-all').disabled=false;
  }catch(error){$('batch-status').textContent=error.message;}
  finally{lockInputs(false);$('stop-all').disabled=true;}
});
$('download-all').addEventListener('click',()=>{
  if(!batchReport)return;
  const url=URL.createObjectURL(new Blob([JSON.stringify(batchReport,null,2)],{type:'application/json'}));
  const link=document.createElement('a');link.href=url;link.download='devtwin-13-investigations.json';link.click();URL.revokeObjectURL(url);
});
