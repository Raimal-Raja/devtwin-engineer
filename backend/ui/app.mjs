import {sessionToken,githubInput} from '/github.mjs';
const $=id=>document.getElementById(id);
let githubSnapshot=null;
let archive='',previewSignature='',report=null,provider='',proposal=null,publicInputRequired=false;
const selection=()=>$('selected').value.split(/\r?\n/).map(x=>x.trim()).filter(Boolean);
const signature=()=>JSON.stringify([archive,selection()]);
function clearPatch(){proposal=null;$('patch').textContent='No current patch.';$('approve-patch').checked=false;$('approve-run').checked=false;$('verification').textContent='No checks executed.';for(const id of ['approve-patch','download-patch','approve-run','verify'])$(id).disabled=true;}
function clearResults(){report=null;clearPatch();$('result').textContent='No current report.';$('repair-result').textContent='No repair loop executed.';$('export').disabled=true;$('approve-loop').checked=false;}
function invalidate(){previewSignature='';provider='';publicInputRequired=false;report=null;clearPatch();$('approve-loop').checked=false;$('repair-result').textContent='No repair loop executed.';$('consent').checked=false;$('investigate').disabled=true;$('propose').disabled=true;$('repair').disabled=true;$('export').disabled=true;$('files').textContent='Selection changed. Preview files again.';$('result').textContent='No current report.';}
function lockInputs(busy){for(const id of ['token','archive','selected','task','workflow','consent','repository','ref','github','github-browse','approve-loop'])$(id).disabled=busy;for(const item of $('github-list').querySelectorAll('input'))item.disabled=busy;for(const id of ['preview','investigate','propose','repair'])$(id).disabled=busy||((id!=='preview')&&!previewSignature);for(const id of ['approve-patch','download-patch','approve-run','verify'])$(id).disabled=busy||!proposal;}
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
    $('github-source').textContent=`${result.repository} · ${result.ref} · ${result.commit} · choose files, then import. ${result.files_truncated?'Showing the first 250 eligible files. ':''}Content is validated during import.`;
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
  if(!proposal||!$('approve-patch').checked||!$('approve-run').checked){$('status').textContent='Approve the reviewed patch and isolated execution before running checks.';return;}
  lockInputs(true);$('status').textContent='Running original and candidate isolated checks…';$('verification').textContent='Verification pending.';
  try{const result=await request('/api/verify',{archive,selected:selection(),patch:proposal.patch,approved:true,execution_approved:true});
    $('verification').textContent=JSON.stringify(result,null,2);$('status').textContent=`Verification ${result.status}. Review actual scope and limitations.`;
  }catch(error){$('verification').textContent='No successful verification report.';$('status').textContent=error.message;}finally{lockInputs(false);}
});
$('repair').addEventListener('click',async()=>{
  if(previewSignature!==signature()||!$('consent').checked||!$('approve-loop').checked){$('status').textContent='Preview files and approve provider submission and the bounded repair loop first.';return;}
  clearResults();lockInputs(true);$('export').disabled=true;$('status').textContent='Running bounded investigation, candidate generation and isolated checks…';$('repair-result').textContent='Repair pending.';
  try{const result=await request('/api/repair',{archive,selected:selection(),task:$('task').value,workflow:$('workflow').value,consent:true,public_input_confirmed:publicInputRequired,provider,loop_approved:true});
    report=result;$('repair-result').textContent=JSON.stringify(result,null,2);$('export').disabled=false;
    $('result').textContent=JSON.stringify(result.analysis,null,2);
    const last=result.attempts?.at(-1);
    if(last&&result.patch){proposal=last.proposal;$('patch').textContent=`${proposal.explanation}\n\n${proposal.diff}\n\nComplete replacement for ${proposal.patch.path}:\n${proposal.patch.replacement}`;$('verification').textContent=JSON.stringify(last.verification,null,2);}
    $('status').textContent=`${result.reason || `Repair ${result.status}.`} Review the evidence and final replacement before export.`;
  }catch(error){$('repair-result').textContent='No successful repair report.';$('status').textContent=error.message;}finally{lockInputs(false);}
});
