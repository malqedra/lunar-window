import {GpuEngine as FactorEngine} from '/src/gpu/engine.ts?qaFactor';
import {GpuEngine as BaselineEngine} from '/src/gpu/engine.ts?qaBaseline';
import {GpuEngine} from '/src/gpu/engine.ts';
import {loadField,fieldCell} from '/src/data/field.ts';
import {loadAppData} from '/src/data/load.ts';

const status=document.getElementById('status');
const results=document.getElementById('results');
const report={status:'running',synthetic:[],realField:null,thermalRegression:[]};
const show=async text=>{status.textContent=text;results.textContent=JSON.stringify(report,null,2);await new Promise(r=>setTimeout(r,20));};
const assert=(ok,message)=>{if(!ok)throw Error(message);};
const tolerance=2e-6;

function makeField(angles,decode,bins) {
  const size=2;
  const horizon=new Uint8Array(bins*size*size);
  for(let a=0;a<bins;a++) for(let i=0;i<4;i++) {
    const angle=Array.isArray(angles[i])?angles[i][a]:angles[i];
    horizon[a*4+i]=Math.round((angle-decode.offsetDeg)/decode.stepDeg);
  }
  return {meta:{extentMeters:250,horizon:{size,cellMeters:250,azimuthBins:bins,observerHeightM:2,decode},heights:{size:2,cellMeters:250,min:0,max:0},slope:{size:2,cellMeters:250}},horizon,heights:new Int16Array(4),slope:new Uint8Array(8)};
}

try {
  const app=await loadAppData(()=>{});
  const cases=[
    {name:'Encoded horizons: below zero, level, 10 degrees, 15 degrees',bins:180,decode:{offsetDeg:-8,stepDeg:0.1},angles:[-8,0,10,15],expected:[0,0,0.0301536896070458,0.0669872981077807]},
    {name:'Analytic full rings: 30, 45, 90, and 0 degrees',bins:180,decode:{offsetDeg:0,stepDeg:1},angles:[30,45,90,0],expected:[0.25,0.5,1,0]},
    {name:'Four azimuth bins with partial obstruction and negative horizons',bins:4,decode:{offsetDeg:-90,stepDeg:1},angles:[[90,0,0,0],[45,-45,45,-45],[30,30,-30,-30],[-10,-10,-10,-10]],expected:[0.25,0.25,0.125,0]},
  ];
  for(const test of cases) {
    await show(test.name);
    const engine=new FactorEngine(makeField(test.angles,test.decode,test.bins),app.ephem);
    try {
      const m=engine.computeThermal(0,1);
      const actual=test.expected.map((_,i)=>m.data[i*4]);
      const maxError=Math.max(...actual.map((v,i)=>Math.abs(v-test.expected[i])));
      assert(actual.every(Number.isFinite)&&maxError<tolerance,`${test.name}: GPU mismatch ${maxError}`);
      report.synthetic.push({name:test.name,azimuthBins:test.bins,expected:test.expected,actual,maxAbsoluteError:maxError,passed:true});
    } finally {engine.dispose();}
  }

  await show('Loading the committed south polar field…');
  const field=await loadField(()=>{});
  const n=field.meta.horizon.size;
  const count=n*n;
  const {azimuthBins,decode}=field.meta.horizon;
  const reference=new Float64Array(count);
  for(let a=0;a<azimuthBins;a++)for(let i=0;i<count;i++) {
    const elevation=Math.max(0,field.horizon[a*count+i]*decode.stepDeg+decode.offsetDeg);
    const sine=Math.sin(elevation*Math.PI/180);
    reference[i]+=sine*sine/azimuthBins;
  }
  await show('Checking all 102,400 GPU cells against the CPU reference…');
  const engine=new FactorEngine(field,app.ephem);
  try {
    const m=engine.computeThermal(0,1);
    let maxError=0,min=Infinity,max=-Infinity;
    for(let i=0;i<count;i++) {
      const value=m.data[i*4];
      assert(Number.isFinite(value)&&value>=0&&value<=1,`Invalid factor at cell ${i}: ${value}`);
      maxError=Math.max(maxError,Math.abs(value-reference[i]));
      min=Math.min(min,value);max=Math.max(max,value);
    }
    assert(maxError<tolerance,`Real-field GPU mismatch: ${maxError}`);
    const floor=app.sites.find(s=>s.id==='shackleton-floor');
    const cell=fieldCell(field,floor.lat,floor.lon);
    const index=cell.row*n+cell.col;
    let lowSlopeIndex=-1;
    for(let i=0;i<count;i++) if(field.slope[i]<=4&&(lowSlopeIndex<0||reference[i]<reference[lowSlopeIndex]))lowSlopeIndex=i;
    const namedSiteFactor=floor.horizon.reduce((sum,h)=>sum+Math.sin(Math.max(0,h)*Math.PI/180)**2,0)/floor.horizon.length;
    report.realField={cells:count,azimuthBins,min,max,maxAbsoluteError:maxError,tolerance,
      shackleton:{...cell,gpu:m.data[index*4],cpu:reference[index],namedSiteFactor},
      openLowSlopeCell:{row:Math.floor(lowSlopeIndex/n),col:lowSlopeIndex%n,slopeDeg:field.slope[lowSlopeIndex]/4,gpu:m.data[lowSlopeIndex*4],cpu:reference[lowSlopeIndex]},passed:true};
    assert(report.realField.shackleton.gpu>0.05&&report.realField.shackleton.gpu<0.15,'Shackleton outside expected range');
    assert(report.realField.openLowSlopeCell.gpu<0.001,'Open low-slope cell not close to zero');
  } finally {engine.dispose();}

  for(const window of [{start:0,hours:720},{start:4800,hours:8760}]) {
    await show(`Comparing final thermal output with baseline: ${window.hours} hours…`);
    const baseline=new BaselineEngine(field,app.ephem);
    let before;
    try {before=baseline.computeThermal(window.start,window.hours);}finally{baseline.dispose();}
    await show(`Comparing final thermal output with baseline: ${window.hours} hours (updated shader)…`);
    const updated=new GpuEngine(field,app.ephem);
    let after;
    try {after=updated.computeThermal(window.start,window.hours);}finally{updated.dispose();}
    let maxDifference=0,different=0;
    for(let i=0;i<before.data.length;i++) {
      assert(Number.isFinite(before.data[i])&&Number.isFinite(after.data[i]),`Non-finite thermal value ${i}`);
      const delta=Math.abs(before.data[i]-after.data[i]);
      if(delta!==0)different++;
      maxDifference=Math.max(maxDifference,delta);
    }
    assert(different===0,`Production thermal outputs changed: ${different} channels, max ${maxDifference}`);
    report.thermalRegression.push({...window,comparedChannels:before.data.length,differentChannels:different,maxAbsoluteDifference:maxDifference,passed:true});
  }
  report.status='passed';
  await fetch('/__task42-report',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(report)});
  status.className='pass';
  await show('PASS · 12 analytic cases, 102,400 terrain cells, and unchanged thermal output');
} catch(error) {
  report.status='failed';report.error=String(error);
  status.className='fail';
  await show('FAILED · '+error);
  await fetch('/__task42-report',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(report)});
  console.error(error);
}
