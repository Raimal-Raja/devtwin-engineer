import test from 'node:test';
import assert from 'node:assert/strict';
import {sessionToken,githubInput} from '../backend/ui/github.mjs';

test('workspace token rejects provider keys and accepts surrounding whitespace',()=>{
  assert.equal(sessionToken(' '+ 'a'.repeat(64)+' '),'a'.repeat(64));
  for(const value of ['', 'sk-or-v1-example','DEVTWIN_SESSION_TOKEN='+'a'.repeat(64)])assert.throws(()=>sessionToken(value),/DEVTWIN_SESSION_TOKEN/);
});
test('GitHub browsing accepts URL alone and importing explains missing file selection',()=>{
  const url='https://github.com/Raimal-Raja/AutoReply-Whatsapp-Bot';
  assert.equal(githubInput(url,'',[],false).ref,'');
  assert.throws(()=>githubInput(url,'',[]),/Select 1/);
  assert.deepEqual(githubInput(url,'main',['chat_utils.py']).selected,['chat_utils.py']);
});
test('GitHub inputs reject foreign hosts, branch URLs, duplicates and excessive selection',()=>{
  for(const url of ['https://evil.example/x/y','https://github.com/x/y/tree/main','x/..'])assert.throws(()=>githubInput(url,'',[],false));
  assert.throws(()=>githubInput('x/y','',['a.py','A.py']),/unique/);
  assert.throws(()=>githubInput('x/y','',Array.from({length:31},(_,i)=>`${i}.py`)),/Select 1/);
});
