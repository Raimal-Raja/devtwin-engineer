const $=id=>document.getElementById(id);
let archive='',previewSignature='',report=null;
const selection=()=>$('selected').value.split(/\r?\n/).map(x=>x.trim()).filter(Boolean);
const signature=()=>JSON.stringify([archive,selection()]);
function invalidate(){previewSignature='';report=null;$('consent').checked=false;$('investigate').disabled=true;$('export').disabled=true;$('files').textContent='Selection changed. Preview files again.';$('result').textContent='No current report.';}
function lockInputs(busy){for(const id of ['token','archive','selected','task','workflow','consent'])$(id).disabled=busy;}
async function request(route,data){
  const response=await fetch(route,{method:'POST',headers:{'Content-Type':'application/json','Authorization':'Bearer '+$('token').value},body:JSON.stringify(data),cache:'no-store'});
  const result=await response.json();
  if(!response.ok)throw new Error(result.error||'Request failed');
  return result;
}
$('archive').addEventListener('change',async()=>{
  archive='';invalidate();const file=$('archive').files[0];if(!file)return;
  if(file.size>2*1024*1024){$('status').textContent='ZIP exceeds 2 MiB.';return;}
  try{const bytes=new Uint8Array(await file.arrayBuffer());let raw='';for(const byte of bytes)raw+=String.fromCharCode(byte);archive=btoa(raw);$('status').textContent='ZIP loaded locally. Select exact file paths and preview.';}catch{$('status').textContent='ZIP could not be loaded.';}
});
$('selected').addEventListener('input',invalidate);
$('preview').addEventListener('click',async()=>{
  invalidate();lockInputs(true);$('preview').disabled=true;$('status').textContent='Validating selection…';
  try{const current=signature();const result=await request('/api/preview',{archive,selected:selection()});if(current!==signature())throw new Error('Selection changed; preview again.');
    $('files').textContent=result.files.map(file=>`${file.path}\nSHA-256: ${file.sha256}\n${file.content}`).join('\n\n');
    $('workflow').replaceChildren(...result.workflows.map(value=>{const option=document.createElement('option');option.value=value;option.textContent=value.replaceAll('-',' ');return option;}));
    $('workflow').disabled=false;previewSignature=current;$('investigate').disabled=false;$('status').textContent='Preview ready. Nothing has been sent to the model.';
  }catch(error){$('status').textContent=error.message;}finally{lockInputs(false);$('workflow').disabled=!previewSignature;$('preview').disabled=false;}
});
$('investigate').addEventListener('click',async()=>{
  if(previewSignature!==signature()||!$('consent').checked){$('status').textContent='Preview current files and approve submission first.';return;}
  const current=signature();lockInputs(true);$('preview').disabled=true;$('investigate').disabled=true;$('status').textContent='Investigating source; no commands or tests are running…';report=null;$('export').disabled=true;
  try{const result=await request('/api/investigate',{archive,selected:selection(),task:$('task').value,workflow:$('workflow').value,consent:true});
    if(current!==signature())throw new Error('Selection changed; discard this response and investigate again.');
    report=result;$('result').textContent=JSON.stringify(result,null,2);$('export').disabled=false;$('status').textContent='Source analysis ready. Findings and proposed checks remain unverified.';
  }catch(error){$('result').textContent='No successful report.';$('status').textContent=error.message;}finally{lockInputs(false);$('preview').disabled=false;$('investigate').disabled=previewSignature!==signature();}
});
$('export').addEventListener('click',()=>{if(!report)return;const url=URL.createObjectURL(new Blob([JSON.stringify(report,null,2)],{type:'application/json'}));const link=document.createElement('a');link.href=url;link.download='devtwin-investigation.json';link.click();URL.revokeObjectURL(url);});
