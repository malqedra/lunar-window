import {readFile,mkdir,writeFile} from 'node:fs/promises';
import {execFileSync} from 'node:child_process';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const work=path.dirname(fileURLToPath(import.meta.url));
const repo=path.resolve(work,'../outputs/lunar-window'),web=path.join(repo,'web');
const output=path.resolve(work,'../outputs/issue-101-verification');
const before=process.argv.includes('--before');
const baseline=execFileSync('git',['show','13d45a9:web/src/App.tsx'],{cwd:repo,encoding:'utf8'});
const baselineScene=execFileSync('git',['show','13d45a9:web/src/three/MoonScene.ts'],{cwd:repo,encoding:'utf8'});
const {createServer}=await import(pathToFileURL(path.join(web,'node_modules/vite/dist/node/index.js')));
const server=await createServer({root:web,configFile:path.join(web,'vite.config.ts'),plugins:[{
  name:'issue101-verification',enforce:'pre',
  resolveId(id){if(id==='/qa-issue101.mjs')return '\0issue101';},
  async load(id){
    if(id==='\0issue101')return readFile(path.join(work,'issue101-browser.mjs'),'utf8');
    if(before&&id.replaceAll('\\','/')===path.join(web,'src/App.tsx').replaceAll('\\','/'))return baseline;
    if(before&&id.replaceAll('\\','/')===path.join(web,'src/three/MoonScene.ts').replaceAll('\\','/'))return baselineScene;
  },
  transformIndexHtml:{order:'pre',handler(html){return html.replace('<script type="module" src="/src/main.tsx"></script>',
    `<script>window.issue101Before=${before}</script><script type="module" src="/qa-issue101.mjs"></script>`);}},
  configureServer(vite){vite.middlewares.use(async(req,res,next)=>{
    if(req.url==='/qa-issue101-report'&&req.method==='POST'){
      let body='';for await(const chunk of req){body+=chunk;if(body.length>100000)throw Error('Large report');}
      const data=JSON.parse(body);await mkdir(output,{recursive:true});
      const name=`${data.before?'before':'after'}-${data.viewport.width}-${data.name}.json`;
      await writeFile(path.join(output,name),JSON.stringify(data,null,2));res.end(name);
    }else next();
  });}
}],server:{host:'127.0.0.1',port:before?5201:5200,strictPort:true}});
await server.listen();server.printUrls();
