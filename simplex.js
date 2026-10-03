(() => {
  const canvas = document.getElementById('simplex-canvas');
  if (!canvas) return;
  const context = canvas.getContext('2d');
  if (!context) return;

  const stages = ['Wake', 'N1', 'N2', 'N3'];
  const colors = ['#b16b2e', '#9a5773', '#207a83', '#565b97'];
  const vertices = [[1, 1, 1], [-1, -1, 1], [-1, 1, -1], [1, -1, -1]];
  const filter = document.getElementById('stage-filter');
  const chooser = document.getElementById('example-select');
  const status = document.getElementById('simplex-status');
  const explanation = document.getElementById('example-explanation');
  const cells = ['prob-wake','prob-n1','prob-n2','prob-n3'].map(id => document.getElementById(id));
  let yaw = -0.45, pitch = 0.18, selected = null, drag = null, plotted = [];
  let cloud = [], examples = [], customSelected = null;

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
    context.lineWidth = emphasis ? 2.8 : 1;
    context.globalAlpha = emphasis ? 1 : .24;
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
      .map(item => ({item, ...projected(item.xyz,width,height)}))
      .sort((a,b) => a.depth-b.depth);
    plotted.forEach(({item,x,y}) => drawMark(x,y,item.stage,1.8,false));
    if (selected) {
      const chosen = projected(selected.xyz,width,height);
      drawMark(chosen.x,chosen.y,selected.stage,6,true);
    }
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
    const scaled = item.p.map(v => v*1000);
    const tenths = scaled.map(Math.floor);
    const order = [0,1,2,3].sort((a,b) => (scaled[b]-tenths[b]) - (scaled[a]-tenths[a]));
    const missing = 1000-tenths.reduce((a,b) => a+b,0);
    for (let i=0;i<missing;i++) tenths[order[i]]++;
    tenths.forEach((v,i) => {cells[i].textContent = (v/10).toFixed(1) + '%';});
    explanation.textContent = description + ' The displayed values sum to 100%.';
    draw();
  }
  function showCustom(item, description, name) {
    let option = chooser.querySelector('option[value="custom"]');
    if (!option) {
      option = document.createElement('option');
      option.value = 'custom';
      chooser.appendChild(option);
    }
    option.textContent = name;
    customSelected = {item, description};
    chooser.value = 'custom';
    show(item, description);
  }
  function argmax(values) {
    return values.reduce((best, value, i) => value > values[best] ? i : best, 0);
  }
  function best(predicate, score) {
    let winner = null, value = -Infinity;
    for (const item of cloud) {
      if (!predicate(item)) continue;
      const current = score(item);
      if (current > value) {winner = item; value = current;}
    }
    return winner;
  }
  function makeExamples() {
    const wake = best(() => true, item => item.p[0]);
    const balance = best(item => {
      const top = item.p.map((_,i) => i).sort((a,b) => item.p[b]-item.p[a]);
      return top[0] < 2 && top[1] < 2;
    }, item => -Math.abs(item.p[0]-item.p[1]) + .1*(item.p[0]+item.p[1])) || wake;
    const n2 = best(() => true, item => item.p[2]);
    const uncertain = best(() => true, item => -Math.max(...item.p));
    examples = [
      {item:wake, name:'Wake-weighted window', description:'A held-out window with relatively high Wake probability.'},
      {item:balance, name:'Wake / N1 balance', description:'A held-out window with similar Wake and N1 probabilities.'},
      {item:n2, name:'N2-weighted window', description:'A held-out window with relatively high N2 probability.'},
      {item:uncertain, name:'More uncertain window', description:'A held-out window with probability spread across stages.'}
    ];
    chooser.replaceChildren();
    customSelected = null;
    examples.forEach((entry,i) => {
      const option = document.createElement('option');
      option.value = String(i);
      option.textContent = entry.name;
      chooser.appendChild(option);
    });
  }
  async function load() {
    try {
      const response = await fetch('assets/sleep-probabilities.json');
      if (!response.ok) throw new Error('HTTP ' + response.status);
      const data = await response.json();
      if (JSON.stringify(data.stages) !== JSON.stringify(stages) ||
          !Array.isArray(data.probabilities) || !data.probabilities.length) {
        throw new Error('Unexpected probability data format');
      }
      cloud = data.probabilities.map((row,index) => {
        if (!Array.isArray(row) || row.length !== 4 ||
            row.some(v => typeof v !== 'number' || !Number.isFinite(v) || v < 0)) {
          throw new Error('Invalid probability row ' + index);
        }
        const sum = row.reduce((a,b) => a+b, 0);
        if (Math.abs(sum-1) > .001) throw new Error('Probability row does not sum to one');
        const p = row.map(v => v/sum);
        return {p,stage:argmax(p),xyz:point3(p)};
      });
      makeExamples();
      status.textContent = cloud.length.toLocaleString() +
        ' anonymized, subject-held-out window predictions. Color and filter show each window’s highest-probability stage.';
      show(examples[0].item,examples[0].description);
      resize();
    } catch (error) {
      status.textContent = 'Probability data could not be loaded. Please reload this page later.';
      explanation.textContent = '';
      console.error('Sleep probability data:',error);
      resize();
    }
  }
  chooser.addEventListener('change', () => {
    if (chooser.value === 'custom' && customSelected) {
      show(customSelected.item,customSelected.description);
      return;
    }
    const entry = examples[Number(chooser.value)];
    if (entry) {
      filter.value = 'all';
      show(entry.item,entry.description);
    }
  });
  filter.addEventListener('change', () => {
    if (filter.value === 'all') {draw(); return;}
    const stage = Number(filter.value);
    if (!selected || selected.stage !== stage) {
      const item = best(candidate => candidate.stage === stage, candidate => candidate.p[stage]);
      if (item) {
        showCustom(item,'A held-out window with ' + stages[stage] + ' as its highest-probability stage.',
          'Selected ' + stages[stage] + ' window');
      } else draw();
    } else draw();
  });
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
      let nearest=null,distance=12*12;
      for (const mark of plotted) {
        const d=(mark.x-x)**2+(mark.y-y)**2;
        if (d<distance) {nearest=mark.item;distance=d;}
      }
      if (nearest) {
        showCustom(nearest,'Selected held-out window; the nearest vertex indicates its largest probability.',
          'Selected plotted window');
      }
    }
    drag=null;
  });
  canvas.addEventListener('pointercancel', () => {drag=null;});
  window.addEventListener('resize', resize);
  load();
})();
