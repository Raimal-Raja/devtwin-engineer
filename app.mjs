import {workflows,filterWorkflows,setupPlan,handoff} from './model.mjs';
const $=id=>document.getElementById(id);
let group='All',runtime='codex';
let noticeTimer;
function notify(message){$('notice').textContent=message;$('notice').classList.add('visible');clearTimeout(noticeTimer);noticeTimer=setTimeout(()=>$('notice').classList.remove('visible'),4000);}
async function copy(text){try{await navigator.clipboard.writeText(text);notify('Copied to clipboard.');}catch{notify('Clipboard unavailable. Select and copy the text manually.');}}
function renderCatalog(){const items=filterWorkflows($('search').value,group);$('workflow-grid').replaceChildren();for(const w of items){const button=document.createElement('button');button.className='workflow-card';button.innerHTML=`<div class="card-top"><span class="card-number">${String(w.number).padStart(2,'0')}</span><span class="card-group">${w.group}</span><span class="card-arrow">↗</span></div><h3>${w.name}</h3><p>${w.description}</p><div class="card-bottom"><span class="${w.maturity==='Core workflow'?'core':'draft'}">${w.maturity}</span><span>Prepare task →</span></div>`;button.addEventListener('click',()=>{$('workflow').value=w.id;$('task').value='';renderPrompt();$('handoff').scrollIntoView({behavior:'smooth'});$('workflow').focus({preventScroll:true});});$('workflow-grid').append(button);}$('result-count').textContent=items.length;$('empty').hidden=items.length>0;}
function renderSetup(){const plan=setupPlan(runtime,$('mode').value,$('os').value);$('commands').textContent=plan.commands;$('install-instructions').textContent=plan.instructions;$('next-step').textContent=plan.next;$('download').href=plan.download;$('download').download=plan.filename;$('download').textContent=`Download ${$('mode').value==='plugin'?'plugin':'skill'} package ↓`;$('runtime-label').textContent=runtime==='codex'?'CODEX':'CLAUDE CODE';$('command-context').textContent=runtime==='claude-code'&&$('mode').value==='plugin'?'CLAUDE CODE SESSION':'TERMINAL';$('official-guide').href=runtime==='codex'?'https://developers.openai.com/plugins/build/plugins':'https://code.claude.com/docs/en/plugins';renderPrompt();}
function renderPrompt(){$('prompt').textContent=handoff(runtime,$('mode').value,$('workflow').value,$('task').value);}
for(const w of workflows){const option=document.createElement('option');option.value=w.id;option.textContent=w.name;$('workflow').append(option);}
$('workflow').value='implementation';
document.querySelectorAll('[data-group]').forEach(button=>button.addEventListener('click',()=>{group=button.dataset.group;document.querySelectorAll('[data-group]').forEach(b=>{const selected=b===button;b.classList.toggle('selected',selected);b.setAttribute('aria-pressed',selected);});renderCatalog();}));
document.querySelectorAll('[data-runtime]').forEach(button=>button.addEventListener('click',()=>{runtime=button.dataset.runtime;document.querySelectorAll('[data-runtime]').forEach(b=>{const selected=b===button;b.classList.toggle('selected',selected);b.setAttribute('aria-pressed',selected);});renderSetup();}));
$('search').addEventListener('input',renderCatalog);$('mode').addEventListener('change',renderSetup);$('os').addEventListener('change',renderSetup);$('workflow').addEventListener('change',renderPrompt);$('generate').addEventListener('click',()=>{renderPrompt();notify('Handoff prepared for your selected runtime.');});$('copy-commands').addEventListener('click',()=>copy($('commands').textContent));$('copy-prompt').addEventListener('click',()=>copy($('prompt').textContent));
$('export-prompt').addEventListener('click',()=>{renderPrompt();const url=URL.createObjectURL(new Blob(['# DevTwin Engineer task\n\n'+$('prompt').textContent+'\n'],{type:'text/markdown'}));const a=document.createElement('a');a.href=url;a.download='devtwin-task.md';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
renderCatalog();renderSetup();

function routePage(){
 const hash=location.hash.slice(1)||'welcome';
 const page=['workflows','catalog','workflow-list','handoff'].includes(hash)?'workflows':hash==='explorer'?'explorer':'welcome';
 document.querySelectorAll('[data-view]').forEach(view=>{view.hidden=view.dataset.view!==page;});
 document.querySelectorAll('[data-page]').forEach(link=>{if(link.dataset.page===page)link.setAttribute('aria-current','page');else link.removeAttribute('aria-current');});
 const anchor=document.getElementById(hash);
 if(anchor)requestAnimationFrame(()=>anchor.scrollIntoView());else window.scrollTo(0,0);
}
window.addEventListener('hashchange',routePage);routePage();
