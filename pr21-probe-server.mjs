import path from 'node:path';
import { pathToFileURL } from 'node:url';

const repo = process.argv[2];
const root = path.join(repo, 'web');
const { createServer } = await import(pathToFileURL(path.join(root, 'node_modules/vite/dist/node/index.js')));
const probe = `
const __qaCounts = { requests: 0, gpu: 0, paints: 0, last: {} };
const __qaModels = new WeakMap();
let __qaNextModel = 0;
function __qaModel(m) { if (!__qaModels.has(m)) __qaModels.set(m, ++__qaNextModel); return __qaModels.get(m); }
function __qaMark(kind, value) {
  __qaCounts[kind]++;
  __qaCounts.last[kind] = value;
  let el = document.getElementById('pr21-probe');
  if (!el) { el = document.createElement('output'); el.id = 'pr21-probe';
    el.style.cssText = 'position:fixed;left:280px;top:270px;max-width:380px;padding:8px;background:white;color:black;font:12px monospace;z-index:9999;pointer-events:none';
    document.body.appendChild(el); }
  el.textContent = JSON.stringify(__qaCounts);
}
`;
const server = await createServer({ root, configFile: path.join(root, 'vite.config.ts'), server: {host:'127.0.0.1',port:5174,strictPort:true}, plugins: [{
  name:'pr21-qa-probe', enforce:'pre',
  transform(code,id) {
    if (!id.replaceAll('\\','/').endsWith('/src/gpu/globalOverlay.ts')) return;
    code = code.replace('const req = globalRequest(layer, hour, rangeDays);', '__qaMark("requests", {layer, hour, rangeDays}); const req = globalRequest(layer, hour, rangeDays);');
    code = code.replace('m = engine.compute(kind, start, hours);', '__qaMark("gpu", {kind, start, hours}); m = engine.compute(kind, start, hours);');
    code = code.replace('const m = await getGlobalMetrics(req.kind, req.start, req.hours);', 'if (new URLSearchParams(location.search).has("slow")) await new Promise((r) => setTimeout(r, 15000)); const m = await getGlobalMetrics(req.kind, req.start, req.hours);');
    code = code.replace('const { layer, m } = source;', 'const { layer, m } = source; __qaMark("paints", {layer, palette, model:__qaModel(m)});');
    return probe + code;
  }
}] });
await server.listen();
console.log('PR 21 probe ready at http://127.0.0.1:5174');
