import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {workflows} from '../backend/ui/batch.mjs';

function shell(hash='#welcome'){
 class Element{
  constructor(){this.children=[];this.events={};this.attrs={};this.dataset={};this.textContent='';}
  append(...nodes){this.children.push(...nodes);}replaceChildren(...nodes){this.children=nodes;}
  setAttribute(k,v){this.attrs[k]=v;}removeAttribute(k){delete this.attrs[k];}
  addEventListener(k,fn){this.events[k]=fn;}click(){this.events.click?.();}
  scrollIntoView(){this.scrolled=true;}focus(){this.focused=true;}querySelectorAll(){return [];}after(){}
 }
 const html=fs.readFileSync(new URL('../backend/ui/index.html',import.meta.url),'utf8'),nodes=new Map();
 for(const [,id] of html.matchAll(/id="([^"]+)"/g))nodes.set(id,new Element());
 const views=[...html.matchAll(/data-view="([^"]+)"/g)].map(([,view])=>Object.assign(new Element(),{dataset:{view}}));
 const links=[...html.matchAll(/data-page="([^"]+)"/g)].map(([,page])=>Object.assign(new Element(),{dataset:{page}}));
 const events={},window={addEventListener:(k,f)=>events[k]=f,scrollTo(){}},location={hash};
 const document={getElementById:id=>nodes.get(id),createElement:()=>new Element(),
  querySelectorAll:q=>q==='[data-view]'?views:links,addEventListener:(k,f)=>events[k]=f};
 const script=fs.readFileSync(new URL('../backend/ui/shell.mjs',import.meta.url),'utf8').replace(/^import [^\n]*\n/,'');
 vm.runInNewContext(script,{document,window,location,workflows,TextEncoder});
 return {nodes,views,links,events,location};
}
test('three views navigate without reloading or clearing the session fields',()=>{
 const s=shell();s.nodes.get('token').value='session';
 assert.equal(s.views.filter(v=>!v.hidden)[0].dataset.view,'welcome');
 s.location.hash='#inspect';s.events.hashchange();
 assert.equal(s.views.filter(v=>!v.hidden)[0].dataset.view,'inspect');
 assert.equal(s.nodes.get('global-status').hidden,false);
 s.location.hash='#workflows';s.events.hashchange();
 assert.equal(s.views.filter(v=>!v.hidden)[0].dataset.view,'workflows');
 assert.equal(s.nodes.get('token').value,'session');
 s.location.hash='#setup';s.events.hashchange();
 assert.equal(s.nodes.get('setup').scrolled,true);
});
test('source explorer preserves literal untrusted content and clears on selection changes',()=>{
 const s=shell('#inspect');s.events['preview-ready']({detail:{files:[{path:'app.py',sha256:'abc',content:'<script>untrusted</script>'}]}});
 assert.match(s.nodes.get('selection-summary').textContent,/1 selected files/);
 assert.match(s.nodes.get('source-view').textContent,/<script>untrusted<\/script>/);
 assert.equal(s.nodes.get('source-view').children.length,0);
 s.events['selection-invalidated']();assert.match(s.nodes.get('source-view').textContent,/Preview the selected/);
 assert.equal(s.nodes.get('workflow-board').children.length,13);
});
