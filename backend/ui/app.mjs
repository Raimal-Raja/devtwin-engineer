const $=id=>document.getElementById(id);
let archive='',previewSignature='',report=null,provider='',proposal=null;
const selection=()=>$('selected').value.split(/\r?\n/).map(x=>x.trim()).filter(Boolean);
const signature=()=>JSON.stringify([archive,selection()]);
function clearPatch(){proposal=null;$('patch').textContent='No current patch.';$('approve-patch').checked=false;$('approve-run').checked=false;$('verification').textContent='No checks executed.';for(const id of ['approve-patch','download-patch','approve-run','verify'])$(id).disabled=true;}
function invalidate(){previewSignature='';provider='';report=null;clearPatch();$('approve-loop').checked=false;$('repair-result').textContent='No repair loop executed.';$('consent').checked=false;$('investigate').disabled=true;$('propose').disabled=true;$('repair').disabled=true;$('export').disabled=true;$('files').textContent='Selection changed. Preview files again.';$('result').textContent='No current report.';}
function lockInputs(busy){for(const id of ['token','archive','selected','task','workflow','consent','repository','ref','github','approve-loop'])$(id).disabled=busy;for(const id of ['preview','investigate','propose','repair'])$(id).disabled=busy||((id!=='preview')&&!previewSignature);for(const id of ['approve-patch','download-patch','approve-run','verify'])$(id).disabled=busy||!proposal;}
async function request(route,data){
  const response=await fetch(route,{method:'POST',headers:{'Content-Type':'application/json','Authorization':'Bearer '+$('token').value},body:JSON.stringify(data),cache:'no-store'});
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
$('github').addEventListener('click',async()=>{
  archive='';invalidate();lockInputs(true);$('status').textContent='Importing selected GitHub files; no model call…';$('github-source').textContent='Import pending.';
  try{const result=await request('/api/github',{repository:$('repository').value.trim(),ref:$('ref').value.trim(),selected:selection()});
    archive=result.archive;$('archive').value='';$('github-source').textContent=`${result.repository} · ${result.commit} · ${result.private?'Private':'Public'} · read-only import. No model submission.`;
    $('status').textContent='GitHub import ready. Preview selected files before provider submission.';
  }catch(error){$('github-source').textContent='No successful GitHub import.';$('status').textContent=error.message;}finally{lockInputs(false);$('workflow').disabled=true;}
});
$('preview').addEventListener('click',async()=>{
  invalidate();lockInputs(true);$('preview').disabled=true;$('status').textContent='Validating selection…';
  try{const current=signature();const result=await request('/api/preview',{archive,selected:selection()});if(current!==signature())throw new Error('Selection changed; preview again.');
    $('files').textContent=result.files.map(file=>`${file.path}\nSHA-256: ${file.sha256}\n${file.content}`).join('\n\n');
    $('workflow').replaceChildren(...result.workflows.map(value=>{const option=document.createElement('option');option.value=value;option.textContent=value.replaceAll('-',' ');return option;}));
    provider=result.provider.id;$('provider-details').textContent=`${result.provider.name} · ${result.provider.model}. ${result.provider.notice} ${result.provider.configured?'':'API key is not configured.'}`;
    $('provider-consent').textContent=`I approve sending these selected, nonconfidential files and my task to ${result.provider.name} under the policy shown above.`;
    $('workflow').disabled=false;previewSignature=current;$('investigate').disabled=false;$('propose').disabled=false;$('status').textContent='Preview ready. Nothing has been sent to the model.';
  }catch(error){$('status').textContent=error.message;}finally{lockInputs(false);$('workflow').disabled=!previewSignature;$('preview').disabled=false;}
});
$('investigate').addEventListener('click',async()=>{
  if(previewSignature!==signature()||!$('consent').checked){$('status').textContent='Preview current files and approve submission first.';return;}
  const current=signature();lockInputs(true);$('preview').disabled=true;$('investigate').disabled=true;$('status').textContent='Investigating source; no commands or tests are running…';report=null;$('export').disabled=true;
  try{const result=await request('/api/investigate',{archive,selected:selection(),task:$('task').value,workflow:$('workflow').value,consent:true,provider});
    if(current!==signature())throw new Error('Selection changed; discard this response and investigate again.');
    report=result;$('result').textContent=JSON.stringify(result,null,2);$('export').disabled=false;$('status').textContent='Source analysis ready. Findings and proposed checks remain unverified.';
  }catch(error){$('result').textContent='No successful report.';$('status').textContent=error.message;}finally{lockInputs(false);$('preview').disabled=false;$('investigate').disabled=previewSignature!==signature();}
});
$('export').addEventListener('click',()=>{if(!report)return;const url=URL.createObjectURL(new Blob([JSON.stringify(report,null,2)],{type:'application/json'}));const link=document.createElement('a');link.href=url;link.download='devtwin-investigation.json';link.click();URL.revokeObjectURL(url);});
$('task').addEventListener('input',clearPatch);
$('propose').addEventListener('click',async()=>{
  if(previewSignature!==signature()||!$('consent').checked){$('status').textContent='Preview current files and approve provider submission first.';return;}
  clearPatch();lockInputs(true);$('status').textContent='Proposing a change; no tests or edits are running…';
  try{proposal=await request('/api/propose',{archive,selected:selection(),task:$('task').value,consent:true,provider});
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
    $('status').textContent='Selected-file candidate exported. No tests ran and the original upload is unchanged.';
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
  clearPatch();lockInputs(true);$('export').disabled=true;$('status').textContent='Running bounded investigation, candidate generation and isolated checks…';$('repair-result').textContent='Repair pending.';
  try{const result=await request('/api/repair',{archive,selected:selection(),task:$('task').value,workflow:$('workflow').value,consent:true,provider,loop_approved:true});
    report=result;$('repair-result').textContent=JSON.stringify(result,null,2);$('export').disabled=false;
    const last=result.attempts?.at(-1);
    if(last&&result.patch){proposal=last.proposal;$('patch').textContent=`${proposal.explanation}\n\n${proposal.diff}\n\nComplete replacement for ${proposal.patch.path}:\n${proposal.patch.replacement}`;$('verification').textContent=JSON.stringify(last.verification,null,2);}
    $('status').textContent=`Repair ${result.status}. Review the evidence and final replacement before export.`;
  }catch(error){$('repair-result').textContent='No successful repair report.';$('status').textContent=error.message;}finally{lockInputs(false);}
});
