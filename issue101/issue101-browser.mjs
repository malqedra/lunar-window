import {SlowPlaybackMonitor} from '/src/lib/playbackPerformance.ts';
const report={before:window.issue101Before,controlledFrameTimestamps:true,controlledVisibility:true,errors:[],samples:0,decisions:[]};
let clock=0,visible=true,pendingTrace=null,gapPerFrame=1000/60;
let measuring=false;
window.addEventListener('error',e=>report.errors.push(e.message));
window.addEventListener('unhandledrejection',e=>report.errors.push(String(e.reason)));
const originalSample=SlowPlaybackMonitor.prototype.sample;
SlowPlaybackMonitor.prototype.sample=function(now){
  report.samples++;
  const trace=pendingTrace;pendingTrace=null;
  let result=null;
  for(let i=0;i<(trace?.count??1);i++){
    clock+=trace?.gap??gapPerFrame;
    const next=originalSample.call(this,clock);
    if(next!==null){result=next;report.decisions.push({now:clock,slow:next});}
  }
  return result;
};
Object.defineProperty(document,'visibilityState',{configurable:true,get:()=>visible?'visible':'hidden'});
await import('/src/main.tsx');
const panel=document.createElement('div');panel.id='issue101-qa';
panel.style.cssText='position:fixed;left:12px;bottom:174px;z-index:30;width:248px;background:#101a2deb;padding:8px;font:10px monospace;color:#bce9e4;border:1px solid #65889d;border-radius:6px';
panel.innerHTML='<b>Issue 101 · Controlled frame history</b><pre id="issue101-status" style="white-space:pre-wrap;max-height:84px;overflow:auto"></pre><button id="qa-slow">Slow trace</button> <button id="qa-healthy">Healthy trace</button> <button id="qa-hide">Hide document</button> <button id="qa-show">Show document</button><input id="qa-name" value="snapshot" aria-label="Evidence name" style="width:110px"><button id="qa-save">Save results</button><button id="qa-gpu">Measure GPU</button>';
document.body.append(panel);
function update(){
  const scene=window.__scene;
  if(scene&&!measuring){scene.loop();cancelAnimationFrame(scene.raf);}
  document.getElementById('qa-gpu').disabled=!scene||measuring;
  const app=window.__app?.getState(),notice=document.querySelector('.quality-notice'),r=notice?.getBoundingClientRect();
  const actions=notice?[...notice.querySelectorAll('button')].map(button=>{
    const b=button.getBoundingClientRect();return{text:button.textContent,receivesPointer:document.elementFromPoint(b.x+b.width/2,b.y+b.height/2)===button};
  }):[];
  Object.assign(report,{clock,visible,sceneReady:!!window.__scene,quality:app?.quality,playing:app?.playing,hour:app?.hour,
    noticeText:notice?.textContent??null,noticeVisible:!!notice&&getComputedStyle(notice).display!=='none',actions,
    noticeRect:r?{x:r.x,y:r.y,width:r.width,height:r.height}:null,
    viewport:{width:innerWidth,height:innerHeight},overflow:document.documentElement.scrollWidth>innerWidth,
    pendingTrace});
  document.getElementById('issue101-status').textContent=JSON.stringify({ready:report.sceneReady,quality:report.quality,
    playing:report.playing,visible,samples:report.samples,notice:report.noticeVisible,errors:report.errors.length});
}
function trace(gap,count){gapPerFrame=gap;pendingTrace={gap,count};update();}
document.getElementById('qa-slow').onclick=()=>trace(100,200);
document.getElementById('qa-healthy').onclick=()=>trace(1000/60,1000);
document.getElementById('qa-hide').onclick=()=>{visible=false;document.dispatchEvent(new Event('visibilitychange'));update();};
document.getElementById('qa-show').onclick=()=>{visible=true;document.dispatchEvent(new Event('visibilitychange'));update();};
document.getElementById('qa-save').onclick=async()=>{update();report.name=document.getElementById('qa-name').value.replace(/[^a-z0-9-]/gi,'');await fetch('/qa-issue101-report',{method:'POST',body:JSON.stringify(report)});};
document.getElementById('qa-gpu').onclick=async()=>{
  const s=window.__scene;if(!s)return;
  const gl=s.renderer.getContext(),ext=gl.getExtension('EXT_disjoint_timer_query_webgl2');
  if(!ext){report.gpu='timer unavailable';update();return;}
  measuring=true;
  const previous={adapt:s.adaptResolution,dpr:s.dpr,ratio:s.renderer.getPixelRatio(),width:s.host.style.width,height:s.host.style.height};
  s.adaptResolution=()=>{};s.host.style.width='1600px';s.host.style.height='900px';
  s.renderer.setPixelRatio(1);s.composer.setPixelRatio(1);s.dpr=1;s.resize();
  // Let the quality change and terrain refinement settle before timing.
  for(let i=0;i<60;i++){s.dirty=true;s.loop();cancelAnimationFrame(s.raf);await new Promise(r=>setTimeout(r,16));}
  const samples=[];
  for(let i=0;i<14;i++){
    const q=gl.createQuery();gl.beginQuery(ext.TIME_ELAPSED_EXT,q);s.composer.render();gl.endQuery(ext.TIME_ELAPSED_EXT);
    while(!gl.getQueryParameter(q,gl.QUERY_RESULT_AVAILABLE))await new Promise(r=>setTimeout(r,20));
    if(!gl.getParameter(ext.GPU_DISJOINT_EXT))samples.push(gl.getQueryParameter(q,gl.QUERY_RESULT)/1e6);
    gl.deleteQuery(q);
  }
  report.gpu={quality:s.quality,warmupFrames:60,width:gl.drawingBufferWidth,height:gl.drawingBufferHeight,samplesMs:samples,medianMs:samples.slice().sort((a,b)=>a-b)[Math.floor(samples.length/2)]};
  s.adaptResolution=previous.adapt;s.host.style.width=previous.width;s.host.style.height=previous.height;
  s.renderer.setPixelRatio(previous.ratio);s.composer.setPixelRatio(previous.ratio);s.dpr=previous.dpr;s.resize();measuring=false;update();
};
setInterval(update,500);update();
