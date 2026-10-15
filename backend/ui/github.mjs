export function sessionToken(value){
  const token=value.trim();
  if(!/^[A-Za-z0-9]{32,}$/.test(token))throw new Error('Enter DEVTWIN_SESSION_TOKEN from .env.docker in Workspace session token. Do not enter your OpenRouter or GitHub API key.');
  return token;
}

export function githubInput(repository,ref,selected,requireFiles=true){
  const repo=repository.trim(),branch=ref.trim();
  let name=repo;
  if(repo.startsWith('https://')){
    const url=new URL(repo);
    if(url.host!=='github.com'||url.search||url.hash||url.username||url.password)throw new Error('Use a plain https://github.com/owner/repository URL.');
    name=url.pathname.replace(/^\/+|\/+$/g,'');
  }
  name=name.replace(/\.git$/,'');
  if(!/^[A-Za-z0-9_-]+\/[A-Za-z0-9_.-]+$/.test(name)||['.','..'].includes(name.split('/')[1]))throw new Error('Enter owner/repository or its GitHub URL, without /tree/branch or a file path.');
  if(branch.length>200||/[\u0000-\u001f]/.test(branch))throw new Error('Branch, tag or commit must contain at most 200 characters.');
  if(requireFiles&&(!selected.length||selected.length>30))throw new Error('Select 1–30 files from Browse repository files, or enter exact paths above before importing.');
  if(requireFiles&&new Set(selected.map(path=>path.toLowerCase())).size!==selected.length)throw new Error('Selected file paths must be unique.');
  return {repository:repo,ref:branch,selected};
}
