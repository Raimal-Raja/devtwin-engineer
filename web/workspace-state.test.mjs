import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {sessionToken,githubInput} from '../backend/ui/github.mjs';

// Exercise production event handlers with an in-memory DOM, without a browser or network.
function workspace(){
  const nodes=new Map();
  function element(){return {value:'',checked:false,disabled:false,textContent:'',files:[],events:{},
    addEventListener(name,fn){this.events[name]=fn;},replaceChildren(){},querySelectorAll(){return [];}};}
  const html=fs.readFileSync(new URL('../backend/ui/index.html',import.meta.url),'utf8');
  for(const match of html.matchAll(/id="([^"]+)"/g))nodes.set(match[1],element());
  const calls=[],responses=[];
  const context=vm.createContext({document:{getElementById:id=>nodes.get(id),createElement:element},
    sessionToken,githubInput,fetch:async(route)=>{calls.push(route);const result=responses.shift();
      if(result instanceof Error)throw result;
      return {ok:true,json:async()=>result};}});
  const script=fs.readFileSync(new URL('../backend/ui/app.mjs',import.meta.url),'utf8').replace(/^\uFEFF?import [^\n]*\n/,'');
  vm.runInContext(script,context);
  nodes.get('token').value='a'.repeat(32);
  nodes.get('selected').value='app.py';
  vm.runInContext("archive='encoded';",context);
  const emit=(id,event='click')=>nodes.get(id).events[event]();
  async function preview(){responses.push({files:[{path:'app.py',content:'pass',sha256:'hash'}],
    workflows:['implementation'],provider:{id:'test',name:'Test',configured:true,notice:'',model:'fake'}});
    await emit('preview');nodes.get('consent').checked=true;}
  return {nodes,calls,responses,emit,preview};
}

test('task and workflow changes clear prior evidence and reset consent',async()=>{
  for(const [id,event] of [['task','input'],['workflow','change']]){
    const w=workspace();await w.preview();
    w.responses.push({status:'unverified_source_analysis',analysis:{summary:'old'}});
    await w.emit('investigate');assert.equal(w.nodes.get('export').disabled,false);
    w.nodes.get('approve-loop').checked=true;w.emit(id,event);
    assert.equal(w.nodes.get('export').disabled,true);
    assert.equal(w.nodes.get('consent').checked,false);
    assert.equal(w.nodes.get('approve-loop').checked,false);
    assert.equal(w.nodes.get('result').textContent,'No current report.');
  }
});

test('repair displays its own analysis and does not claim an unobserved fix',async()=>{
  const w=workspace();await w.preview();w.nodes.get('approve-loop').checked=true;
  w.responses.push({status:'checks_passed_no_demonstrated_fix',reason:'No baseline failure was resolved.',
    analysis:{analysis:{summary:'current analysis'}},attempts:[],patch:null});
  await w.emit('repair');
  assert.match(w.nodes.get('result').textContent,/current analysis/);
  assert.match(w.nodes.get('status').textContent,/No baseline failure/);
  assert.equal(w.nodes.get('approve-loop').checked,false);
  assert.equal(w.nodes.get('download-patch').disabled,true);
});

test('a failed new investigation removes old downloadable evidence and releases controls',async()=>{
  const w=workspace();await w.preview();w.responses.push({analysis:{summary:'old'}});
  await w.emit('investigate');w.responses.push(new Error('Provider unavailable'));
  await w.emit('investigate');
  assert.equal(w.nodes.get('result').textContent,'No successful report.');
  assert.equal(w.nodes.get('export').disabled,true);
  assert.equal(w.nodes.get('token').disabled,false);
  assert.match(w.nodes.get('status').textContent,/Provider unavailable/);
});

test('proposal execution and export require review and explicit execution consent',async()=>{
  const w=workspace();await w.preview();
  w.responses.push({explanation:'Proposed change',diff:'diff',patch:{path:'app.py',replacement:'value=1'}});
  await w.emit('propose');
  const before=w.calls.length;
  await w.emit('verify');await w.emit('download-patch');
  assert.equal(w.calls.length,before);
  w.nodes.get('approve-patch').checked=true;await w.emit('verify');
  assert.equal(w.calls.length,before);
  w.nodes.get('approve-run').checked=true;
  w.responses.push({status:'passed',observed_failure_resolved:false});await w.emit('verify');
  assert.equal(w.calls.at(-1),'/api/verify');
  w.emit('task','input');
  assert.equal(w.nodes.get('approve-patch').checked,false);
  assert.equal(w.nodes.get('approve-run').checked,false);
  assert.equal(w.nodes.get('verify').disabled,true);
});
