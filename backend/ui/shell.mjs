import {workflows} from '/batch.mjs';
const $=id=>document.getElementById(id);
function route(){
 const page=location.hash.slice(1),view=['inspect','workflows'].includes(page)?page:'welcome';
 if(page==='main'){document.getElementById('main').focus();return;}
 $('global-status').hidden=view==='welcome';
 for(const node of document.querySelectorAll('[data-view]'))node.hidden=node.dataset.view!==view;
 for(const link of document.querySelectorAll('[data-page]')){
  if(link.dataset.page===view)link.setAttribute('aria-current','page');else link.removeAttribute('aria-current');
 }
 document.title=`DevTwin — ${view==='welcome'?'Your engineering perspective':view==='inspect'?'Project explorer':'Engineering workflows'}`;
 if(page==='setup')$('setup').scrollIntoView();else if(page!=='main')window.scrollTo(0,0);
}
window.addEventListener('hashchange',route);route();
const cards=new Map();
for(const [i,w] of workflows.entries()){
 const article=document.createElement('article');article.className='workflow-card';article.dataset.status='ready';
 const state=document.createElement('small');state.textContent=`${String(i+1).padStart(2,'0')} / READY`;
 const heading=document.createElement('h3');heading.textContent=w.name;
 const description=document.createElement('p');description.textContent=w.description;
 const details=document.createElement('details');details.hidden=true;
 const summary=document.createElement('summary');summary.textContent='Review source report';
 const output=document.createElement('pre');details.append(summary,output);article.append(state,heading,description,details);
 $('workflow-board').append(article);cards.set(w.id,{article,state,description,details,output,index:i+1});
}
document.addEventListener('batch-progress',event=>{
 const item=event.detail,card=cards.get(item.id);if(!card)return;
 card.article.dataset.status=item.status;card.state.textContent=`${String(card.index).padStart(2,'0')} / ${item.status.toUpperCase()}`;
 if(item.report||item.error){card.details.hidden=false;card.output.textContent=JSON.stringify(item.report||{error:item.error},null,2);}
 $('batch-progress').value=item.completed;
});
document.addEventListener('selection-invalidated',()=>{
 $('selection-summary').textContent='Selection changed. Preview again to inspect the current files.';
 $('source-list').textContent='No current preview.';$('source-view').textContent='Preview the selected files to inspect their source.';
});
document.addEventListener('batch-reset',()=>{
 for(const c of cards.values()){c.article.dataset.status='ready';c.state.textContent=`${String(c.index).padStart(2,'0')} / READY`;c.details.hidden=true;c.output.textContent='';}
});
document.addEventListener('preview-ready',event=>{
 const files=event.detail.files,total=files.reduce((sum,f)=>sum+new TextEncoder().encode(f.content).length,0);
 $('selection-summary').textContent=`${files.length} selected files · ${total.toLocaleString()} UTF-8 bytes · ${files.filter(f=>/(^|\/)test[^/]*\.py$/.test(f.path)).length} Python test modules. Source remains unchanged.`;
 $('source-list').replaceChildren();let buttons=[];
 for(const file of files){
  const button=document.createElement('button');button.type='button';button.textContent=file.path;
  button.addEventListener('click',()=>{for(const b of buttons)b.setAttribute('aria-pressed',String(b===button));$('source-view').textContent=`${file.path}\nSHA-256: ${file.sha256}\n\n${file.content}`;});
  buttons.push(button);$('source-list').append(button);
 }
 if(buttons.length)buttons[0].click();
});
for(const pre of $('setup').querySelectorAll('pre')){
 const button=document.createElement('button');button.type='button';button.className='secondary';button.textContent='Copy commands';
 button.addEventListener('click',async()=>{try{await navigator.clipboard.writeText(pre.textContent);button.textContent='Copied ✓';}catch{button.textContent='Select and copy the commands above';}});
 pre.after(button);
}
