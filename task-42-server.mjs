import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { execFileSync } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const work = path.dirname(fileURLToPath(import.meta.url));
const repository = path.resolve(process.argv[2] || path.join(work, '../outputs/lunar-window'));
const output = path.resolve(process.argv[3] || path.join(work, '../outputs/task-42-verification'));
const web = path.join(repository, 'web');
const baselineRevision = '515b6b0';
const originalThermal = execFileSync('git', ['show', `${baselineRevision}:web/src/gpu/thermal.ts`], {cwd:repository,encoding:'utf8'});
const productionOutput = 'outColor = vec4(tMax, tSum / max(nRec, 1.0), tMin, iceDepth);';
const { createServer } = await import(pathToFileURL(path.join(web,'node_modules/vite/dist/node/index.js')));
const server = await createServer({
  root: web,
  configFile: path.join(web,'vite.config.ts'),
  plugins: [{
    name: 'task-42-verification',
    enforce: 'pre',
    resolveId(id) { if (id === '/__task42-check.mjs') return '\0task-42-check'; },
    async load(id) {
      if (id === '\0task-42-check') return readFile(path.join(work,'task-42-check.mjs'),'utf8');
      const [filename,query] = id.replaceAll('\\','/').split('?');
      if (!query || !['qaFactor','qaBaseline'].includes(query)) return;
      if (filename === path.join(web,'src/gpu/engine.ts').replaceAll('\\','/')) {
        const source = await readFile(filename,'utf8');
        return source.replace('from "./thermal"', `from "/src/gpu/thermal.ts?${query}"`);
      }
      if (filename === path.join(web,'src/gpu/thermal.ts').replaceAll('\\','/')) {
        if (query === 'qaBaseline') return originalThermal;
        const source = await readFile(filename,'utf8');
        if (!source.includes(productionOutput)) throw Error('Thermal output marker changed');
        return source.replace(productionOutput,'outColor = vec4(F, 0.0, 0.0, 1.0);');
      }
    },
    configureServer(vite) {
      vite.middlewares.use(async (req,res,next) => {
        if (req.url === '/__task42-report' && req.method === 'POST') {
          let body='';
          for await (const part of req) {body+=part; if(body.length>1_000_000) throw Error('Oversized report');}
          const report=JSON.parse(body);
          report.baselineRevision=baselineRevision;
          await mkdir(output,{recursive:true});
          await writeFile(path.join(output,'gpu-report.json'),JSON.stringify(report,null,2));
          res.end('saved');
        } else if (req.url === '/__task42.html') {
          res.setHeader('Content-Type','text/html');
          res.end(await vite.transformIndexHtml(req.url, `<!doctype html><meta charset="utf-8"><title>Task 42 GPU verification</title><style>body{background:#0d1421;color:#dce3ee;font:16px/1.5 system-ui;max-width:1000px;margin:36px auto;padding:0 24px}h1{font-size:26px}pre{font:13px/1.45 monospace;white-space:pre-wrap;background:#141f32;padding:20px;border-radius:12px}.pass{color:#71e3ac}.fail{color:#ff8793}</style><h1>Task 42 · Terrain view factor</h1><p id="status">Loading GPU checks…</p><pre id="results"></pre><script type="module" src="/__task42-check.mjs"></script>`));
        } else next();
      });
    },
  }],
  server:{host:'127.0.0.1',port:5173,strictPort:true},
});
await server.listen();
console.log('App: http://127.0.0.1:5173/');
console.log('GPU checks: http://127.0.0.1:5173/__task42.html');
