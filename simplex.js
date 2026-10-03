(() => {
  const canvas = document.getElementById('simplex-canvas');
  if (!canvas) return;
  const context = canvas.getContext('2d');
  if (!context) return;

  const stages = ['Wake', 'N1', 'N2', 'N3'];
  const colors = ['#b16b2e', '#9a5773', '#207a83', '#565b97'];
  const vertices = [[1, 1, 1], [-1, -1, 1], [-1, 1, -1], [1, -1, -1]];
  const descriptions = [
    'Most of the probability mass is near the Wake vertex.',
    'The estimate sits between Wake and N1, so neither stage is decisive.',
    'A point near N2 reflects a comparatively confident N2 estimate.',
    'A point near the center represents uncertainty spread across all four stages.'
  ];
  const examples = [
    {p:[0.78,0.12,0.07,0.03], stage:0, name:'Mostly Wake'},
    {p:[0.46,0.43,0.08,0.03], stage:1, name:'Wake / N1 transition'},
    {p:[0.05,0.10,0.78,0.07], stage:2, name:'Mostly N2'},
    {p:[0.28,0.24,0.27,0.21], stage:3, name:'Uncertain among stages'}
  ];
  const filter = document.getElementById('stage-filter');
  const chooser = document.getElementById('example-select');
  const explanation = document.getElementById('example-explanation');
  const cells = ['prob-wake','prob-n1','prob-n2','prob-n3'].map(id => document.getElementById(id));
  let yaw = -0.45, pitch = 0.18, selected = examples[0], drag = null, plotted = [];

  let seed = 3814;
  const random = () => {
    seed = (1664525 * seed + 1013904223) >>> 0;
    return seed / 4294967296;
  };
  const cloud = [];
  for (let stage = 0; stage < 4; stage++) {
    for (let i = 0; i < 46; i++) {
      const weights = Array.from({length:4}, () => 0.05 + random() * 0.36);
      weights[stage] += 0.45 + random() * 1.25;
      if (i % 7 === 0) weights[(stage + 1) % 4] += 0.45;
      const sum = weights.reduce((a,b) => a+b, 0);
      cloud.push({p:weights.map(v => v / sum), stage, name:'Illustrative point'});
    }
  }

  function point3(p) {
    return [0,1,2].map(axis => p.reduce((sum, probability, i) => sum + probability * vertices[i][axis], 0));
  }
  function rotate(point) {
    const [x,y,z] = point;
    const cy = Math.cos(yaw), sy = Math.sin(yaw), cp = Math.cos(pitch), sp = Math.sin(pitch);
    const x1 = x * cy + z * sy;
    const z1 = -x * sy + z * cy;
    return [x1, y * cp - z1 * sp, y * sp + z1 * cp];
  }
  function projected(point, width, height) {
    const [x,y,z] = rotate(point);
    const scale = Math.min(width * .31, height * .33);
    return {x:width/2 + x*scale, y:height/2 - y*scale, depth:z};
  }
  function drawMark(x,y,stage,size,emphasis) {
    context.strokeStyle = colors[stage];
    context.fillStyle = colors[stage];
    context.lineWidth = emphasis ? 2.8 : 1.5;
    context.globalAlpha = emphasis ? 1 : .65;
    context.beginPath();
    if (stage === 0) context.arc(x,y,size,0,Math.PI*2);
    if (stage === 1) {context.moveTo(x,y-size);context.lineTo(x+size,y);context.lineTo(x,y+size);context.lineTo(x-size,y);context.closePath();}
    if (stage === 2) context.rect(x-size,y-size,size*2,size*2);
    if (stage === 3) {context.moveTo(x-size,y-size);context.lineTo(x+size,y+size);context.moveTo(x+size,y-size);context.lineTo(x-size,y+size);}
    if (stage === 3) context.stroke(); else context.fill();
    if (emphasis) {
      context.globalAlpha = 1;
      context.strokeStyle = '#172126';
      context.beginPath();
      context.arc(x,y,size+4,0,Math.PI*2);
      context.stroke();
    }
    context.globalAlpha = 1;
  }
  function resize() {
    const rect = canvas.getBoundingClientRect();
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.round(rect.width * dpr);
    canvas.height = Math.round(rect.height * dpr);
    context.setTransform(dpr,0,0,dpr,0,0);
    draw();
  }
  function draw() {
    const width = canvas.clientWidth, height = canvas.clientHeight;
    context.clearRect(0,0,width,height);
    context.fillStyle = '#ffffff';
    context.fillRect(0,0,width,height);
    const corner = vertices.map(v => projected(v,width,height));
    const edges = [[0,1],[0,2],[0,3],[1,2],[1,3],[2,3]];
    context.strokeStyle = '#cbd6d3';
    context.lineWidth = 1.4;
    edges.forEach(([a,b]) => {
      context.beginPath();
      context.moveTo(corner[a].x,corner[a].y);
      context.lineTo(corner[b].x,corner[b].y);
      context.stroke();
    });
    const stageFilter = filter.value;
    plotted = cloud.filter(item => stageFilter === 'all' || item.stage === Number(stageFilter))
      .map(item => ({item, ...projected(point3(item.p),width,height)}))
      .sort((a,b) => a.depth-b.depth);
    plotted.forEach(({item,x,y}) => drawMark(x,y,item.stage,3.5,false));
    const chosen = projected(point3(selected.p),width,height);
    drawMark(chosen.x,chosen.y,selected.stage,6,true);
    context.font = '600 13px -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif';
    context.textBaseline = 'middle';
    corner.forEach(({x,y},i) => {
      context.fillStyle = colors[i];
      context.beginPath();
      context.arc(x,y,5,0,Math.PI*2);
      context.fill();
      const nearRight = x > width - 48;
      const nearLeft = x < 48;
      context.textAlign = nearRight ? 'right' : (nearLeft ? 'left' : (x >= width/2 ? 'left' : 'right'));
      const labelX = nearRight ? x - 11 : (nearLeft ? x + 11 : x + (x >= width/2 ? 10 : -10));
      context.fillStyle = '#172126';
      context.fillText(stages[i],labelX,Math.max(14,Math.min(height-14,y)));
    });
  }
  function show(item, description) {
    selected = item;
    const formatted = item.p.slice(0,3).map(v => Math.round(v*1000)/10);
    formatted.push(Math.round((100-formatted.reduce((a,b) => a+b,0))*10)/10);
    formatted.forEach((v,i) => {cells[i].textContent = v.toFixed(1) + '%';});
    explanation.textContent = description + ' The four values sum to 100%.';
    draw();
  }
  chooser.addEventListener('change', () => show(examples[Number(chooser.value)], descriptions[Number(chooser.value)]));
  filter.addEventListener('change', draw);
  [['rotate-left',-.18,0],['rotate-right',.18,0],['rotate-up',0,.14],['rotate-down',0,-.14]].forEach(([id,dy,dp]) => {
    document.getElementById(id).addEventListener('click', () => {
      yaw += dy; pitch = Math.max(-1.2,Math.min(1.2,pitch+dp)); draw();
    });
  });
  document.getElementById('reset-view').addEventListener('click', () => {yaw=-.45;pitch=.18;draw();});
  canvas.addEventListener('pointerdown', event => {
    drag = {x:event.clientX,y:event.clientY,moved:false};
    canvas.setPointerCapture(event.pointerId);
  });
  canvas.addEventListener('pointermove', event => {
    if (!drag) return;
    const dx=event.clientX-drag.x, dy=event.clientY-drag.y;
    if (Math.abs(dx)+Math.abs(dy)>2) drag.moved=true;
    yaw += dx*.009; pitch=Math.max(-1.2,Math.min(1.2,pitch+dy*.009));
    drag.x=event.clientX;drag.y=event.clientY;draw();
  });
  canvas.addEventListener('pointerup', event => {
    if (drag && !drag.moved) {
      const rect=canvas.getBoundingClientRect();
      const x=event.clientX-rect.left,y=event.clientY-rect.top;
      let nearest=null,distance=14*14;
      for (const mark of plotted) {
        const d=(mark.x-x)**2+(mark.y-y)**2;
        if (d<distance) {nearest=mark.item;distance=d;}
      }
      if (nearest) {
        chooser.value='';
        show(nearest,'A selected synthetic point; its closest stage vertex indicates its largest probability.');
      }
    }
    drag=null;
  });
  canvas.addEventListener('pointercancel', () => {drag=null;});
  window.addEventListener('resize', resize);
  show(examples[0],descriptions[0]);
  resize();
})();
