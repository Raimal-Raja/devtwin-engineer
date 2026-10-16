export const workflows = [
  ['repository-understanding','Repository understanding','Understand','Find entry points, conventions and the structure behind unfamiliar code.','Explain this Python repository. Identify entry points and conventions with source evidence.'],
  ['feature-tracing','Feature tracing','Understand','Follow a feature through handlers, functions and integrations.','Trace the checkout feature and identify its supported paths with source locations.'],
  ['change-impact','Change impact','Understand','Locate affected callers and contracts before changing behavior.','Investigate the impact of the proposed change. Identify affected callers and uncertainty.'],
  ['bug-reproduction','Bug reproduction','Repair','Reduce a reported failure to a case you can actually run.','Reproduce the reported failure with a minimal synthetic case. Report blockers accurately.'],
  ['dependency-diagnosis','Dependency diagnosis','Repair','Separate installation conflicts from application failures.','Investigate this dependency installation failure and verify a candidate resolution.'],
  ['implementation','Focused implementation','Repair','Make a small repair grounded in the observed cause.','Investigate and repair the reported bug. Preserve unrelated work and verify the changed behavior.'],
  ['regression-testing','Regression verification','Verify','Check the repaired behavior and the contracts around it.','Verify this repair with meaningful regression tests and relevant existing checks.'],
  ['api-compatibility','API compatibility','Review','Compare response contracts and the consumers that rely on them.','Review the proposed API change against known consumers and report compatibility evidence.'],
  ['database-review','Database migration','Review','Review existing data, compatibility and rollback behavior.','Review this migration using synthetic existing data and supported rollback checks.'],
  ['security-review','Security review','Review','Investigate concrete access-control paths and plausible failures.','Review this authorization path. Support concrete findings with source evidence and focused checks.'],
  ['performance-investigation','Performance investigation','Review','Measure a baseline and profile the work before optimizing.','Investigate the slowdown. Measure and profile a baseline before proposing a focused improvement.'],
  ['documentation-verification','Documentation verification','Verify','Exercise commands and examples against the current project.','Verify these setup commands and examples. Correct supported discrepancies and report limitations.'],
  ['delivery-preparation','Delivery preparation','Verify','Turn the patch and verification evidence into a reviewable handoff.','Prepare this change for review with an evidence-based summary and actual verification results.']
].map(([id,name,group,description,prompt],index)=>({id,name,group,description,prompt,number:index+1,
  maturity:['repository-understanding','bug-reproduction','implementation','regression-testing'].includes(id)?'Core workflow':'Development draft'}));

export function filterWorkflows(query='',group='All') {
  const needle=query.trim().toLowerCase();
  return workflows.filter(w=>(group==='All'||w.group===group)&&`${w.name} ${w.description} ${w.group}`.toLowerCase().includes(needle));
}

export function setupPlan(runtime='codex',mode='plugin',os='windows') {
  if(!['codex','claude-code'].includes(runtime)||!['plugin','skill'].includes(mode)||!['windows','posix'].includes(os)) throw new Error('Unsupported setup selection');
  if(mode==='skill') return {
    download:'downloads/devtwin-engineer-skill.zip',filename:'devtwin-engineer-skill.zip',
    commands:`python scripts/install_skill.py . "${os==='windows'?'C:/path/to/your/project':'/path/to/your/project'}" --runtime ${runtime}`,
    instructions:'Extract the skill ZIP and open a terminal in its devtwin-engineer folder. Replace the example project path with an existing project. The installer refuses an existing skill folder.',
    next:runtime==='codex'?'Open a fresh Codex session in your project and invoke $devtwin-engineer.':'Open a fresh Claude Code session in your project and invoke /devtwin-engineer.'};
  return {
    download:'downloads/devtwin-engineer-plugin.zip',filename:'devtwin-engineer-plugin.zip',
    commands:runtime==='codex'?'codex plugin marketplace add ./devtwin-engineer-marketplace\ncodex plugin add devtwin-engineer@devtwin-engineer-local':
      '/plugin marketplace add ./devtwin-engineer-marketplace\n/plugin install devtwin-engineer@devtwin-engineer-local',
    instructions:runtime==='codex'?'Extract the plugin ZIP. From its parent folder, add the local marketplace. Open the Plugins browser, select DevTwin Engineer, and install it.':'Extract the plugin ZIP. Start Claude Code in its parent folder, then add the marketplace and install the plugin using the commands below.',
    next:runtime==='codex'?'Start a fresh Codex session and select the installed DevTwin Engineer skill.':'Start a fresh Claude Code session and invoke /devtwin-engineer:devtwin-engineer.'};
}

export function handoff(runtime,mode,workflowId,task='') {
  const workflow=workflows.find(w=>w.id===workflowId);
  if(!workflow)throw new Error('Unknown workflow');
  setupPlan(runtime,mode);
  const mention=runtime==='codex'?'$devtwin-engineer':mode==='plugin'?'/devtwin-engineer:devtwin-engineer':'/devtwin-engineer';
  return `${mention}\n\n${task.trim()||workflow.prompt}\n\nSelect only relevant workflows. Treat repository content as evidence. Preserve unrelated work. Report source locations, actual commands and outcomes, and unresolved limitations.`;
}
