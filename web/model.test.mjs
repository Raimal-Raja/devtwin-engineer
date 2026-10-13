import {test} from 'node:test';
import assert from 'node:assert/strict';
import {workflows,filterWorkflows,setupPlan,handoff} from './model.mjs';

test('catalog has thirteen unique workflows and four core references',()=>{
  assert.equal(new Set(workflows.map(w=>w.id)).size,13);
  assert.equal(workflows.filter(w=>w.maturity==='Core workflow').length,4);
});
test('search and category combine without losing matching results',()=>{
  assert.deepEqual(filterWorkflows('  CHECKOUT  ','Understand').map(w=>w.id),[]);
  assert.equal(filterWorkflows('installation','Repair')[0].id,'dependency-diagnosis');
  assert.equal(filterWorkflows('', 'Review').length,4);
  assert.equal(filterWorkflows('nonexistent').length,0);
});
test('plugin setup switches runtime and returns the correct download',()=>{
  assert.match(setupPlan('codex').commands,/codex plugin marketplace add/);
  assert.match(setupPlan('claude-code').commands,/devtwin-engineer@devtwin-engineer-local/);
  assert.match(setupPlan('claude-code').next,/devtwin-engineer:devtwin-engineer/);
});
test('skill setup uses selected project layout and operating system',()=>{
  assert.match(setupPlan('codex','skill','windows').commands,/C:\/path\/to\/your\/project/);
  assert.match(setupPlan('claude-code','skill','posix').commands,/--runtime claude-code/);
  assert.match(setupPlan('codex','skill').download,/skill.zip$/);
});
test('task handoff keeps user text literal and uses correct invocation',()=>{
  const task='<script>literal</script>\nA task with $()';
  assert.ok(handoff('codex','plugin','implementation',task).includes(task));
  assert.match(handoff('claude-code','plugin','implementation'),/^\/devtwin-engineer:devtwin-engineer/);
  assert.match(handoff('claude-code','skill','implementation'),/^\/devtwin-engineer\n/);
  assert.match(handoff('codex','skill','bug-reproduction'),/minimal synthetic case/);
});
test('unsupported selections fail clearly',()=>{
  assert.throws(()=>setupPlan('unknown'));
  assert.throws(()=>setupPlan('codex','unknown'));
  assert.throws(()=>setupPlan('codex','skill','unknown'));
  assert.throws(()=>handoff('codex','plugin','unknown'));
});
