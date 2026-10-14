// Deterministic vector studies. No raster assets, external libraries, or animation.
(() => {
  const NS = 'http://www.w3.org/2000/svg';
  const el = (tag, attrs = {}) => {
    const node = document.createElementNS(NS, tag);
    for (const [key, value] of Object.entries(attrs)) node.setAttribute(key, value);
    return node;
  };
  const add = (parent, tag, attrs = {}) => { const node = el(tag, attrs); parent.append(node); return node; };
  const path = (parent, d, attrs = {}) => add(parent, 'path', { d, ...attrs });
  const portrait = 'M 72 240 C 54 217 49 184 55 149 C 65 95 104 63 160 61 C 214 60 252 92 261 144 C 265 168 261 187 269 199 C 276 210 291 220 295 227 C 297 232 288 237 279 238 L 273 242 C 281 250 276 255 266 257 C 273 265 268 271 258 273 C 266 285 257 291 247 293 C 231 296 219 291 211 287 C 196 301 193 320 203 337 C 220 353 249 359 282 374 L 285 405 L 27 405 L 31 377 C 64 362 89 349 101 326 C 111 307 105 284 89 263 C 82 254 76 247 72 240 Z';
  const hair = 'M 54 175 C 52 116 90 73 145 62 C 189 52 236 77 253 115 C 232 105 211 111 196 122 C 178 112 159 116 145 130 C 124 127 105 135 93 151 C 75 153 62 161 54 175 Z';
  const hairline = 'M 58 181 C 73 162 91 164 103 153 C 115 137 130 135 148 139 C 164 118 182 121 197 131 C 214 116 234 115 255 128';
  const eye = 'M 222 203 Q 238 213 252 204';
  const brow = 'M 221 193 Q 237 186 253 194';
  const lips = 'M 260 269 Q 269 273 277 269';
  const neck1 = 'M 211 287 C 182 317 188 341 203 361';
  const neck2 = 'M 101 323 C 122 346 154 359 183 364';
  const drape = 'M 31 381 C 95 363 108 368 148 385 C 188 402 233 374 282 383';
  const colors = [
    { bg:'#f5f2eb', border:'#a8aba1', fill:'#e1ded4', shade:'#456d67', ink:'#293f3d', accent:'#aa785a', mist:'#c6c4b9', dots:'#758d82' },
    { bg:'#152c36', border:'#a9b5aa', fill:'#c5d2c6', shade:'#6b8982', ink:'#314b49', accent:'#d1ad77', mist:'#3c5860', dots:'#6d9188' },
    { bg:'#e9eee8', border:'#567469', fill:'#c0d4c7', shade:'#2d5c55', ink:'#25443f', accent:'#a16e58', mist:'#c8d9ce', dots:'#7eaaa0' },
    { bg:'#f6eee3', border:'#b9947c', fill:'#e6cfba', shade:'#8f614e', ink:'#6d4c41', accent:'#bd7c58', mist:'#dfc6ad', dots:'#aa8873' }
  ];

  // Face profile measured from the supplied photo by scripts/trace_profile.py.
  // The front contour is extracted from pixels; the hairline (ending at the temple)
  // and jaw are interpreted landmarks. Only the rear skull and bust are drawn by hand.
  const tracedFront = [
    [132.04,56.8],[125.52,62.92],[101.28,104.4],[87.72,120.04],
    [81.38,137.04],[75.86,141.8],[73.98,147.24],[69.82,152],
    [69.34,157.44],[75.38,167.64],[74.68,171.04],[59.59,184.64],
    [45.02,201.64],[44.1,209.12],[45.54,212.52],[57.09,217.28],
    [59.98,220.68],[58.84,237],[61.51,242.44],[59.54,249.24],
    [65.76,258.08],[61.64,262.84],[59.54,276.44],[60.94,279.84],
    [69.74,288]
  ];
  const tracedHairline = [
    [102.2,109.84],[112.7,104.4],[124.6,101.68],[135.8,105.76],
    [147.7,115.96],[154,129.56],[163.1,143.16],[173.6,157.44]
  ];
  const tracedJaw = [
    [82.6,290.72],[103.6,292.76],[122.5,288],[140.7,276.44],
    [156.1,262.84],[170.1,245.16]
  ];
  const smoothPath = points => {
    let d = `M ${points[0][0]} ${points[0][1]}`;
    for (let i = 0; i < points.length - 1; i++) {
      const before = points[Math.max(0, i - 1)];
      const start = points[i];
      const end = points[i + 1];
      const after = points[Math.min(points.length - 1, i + 2)];
      const c1 = [start[0] + (end[0] - before[0]) / 6, start[1] + (end[1] - before[1]) / 6];
      const c2 = [end[0] - (after[0] - start[0]) / 6, end[1] - (after[1] - start[1]) / 6];
      d += ` C ${c1[0].toFixed(2)} ${c1[1].toFixed(2)} ${c2[0].toFixed(2)} ${c2[1].toFixed(2)} ${end[0]} ${end[1]}`;
    }
    return d;
  };
  const bustPath = smoothPath([...tracedFront, ...tracedJaw]) +
    ' C 155 268 149 304 141 329 C 112 353 70 374 27 390 L 27 407 L 294 407 L 290 389 C 267 377 247 359 241 333 C 238 317 239 301 245 284 C 268 264 282 232 287 196 C 293 148 274 101 235 72 C 214 58 198 53 180 51 C 161 48 145 51 132.04 56.8 Z';
  const hairCapPath = 'M 102.2 109.84 C 112 78 125 57 132.04 56.8 C 145 51 161 48 180 51 C 198 53 214 58 235 72 C 274 101 293 148 287 196 C 282 232 268 264 245 284 C 218 260 213 223 208 202 C 201 181 187 166 173.6 157.44 ' +
    smoothPath([...tracedHairline].reverse()).replace(/^M [^C]+/, '') + ' Z';

  function drawNightOracle(svg, c, mode = 'base') {
    const hairline = tracedHairline;
    const jaw = tracedJaw;
    const maskPath = smoothPath([...tracedFront.slice(2), ...jaw]) +
      ' C 181 222 182 184 173.6 157.44 ' +
      smoothPath([...hairline].reverse()).replace(/^M [^C]+/, '') + ' Z';
    const ink = '#304744';
    const stone = '#c8d4c7';
    const light = '#e5e9df';

    const star = (x,y,r,color,opacity=1) => path(svg,
      `M ${x} ${y-r} L ${x+r*.18} ${y-r*.18} L ${x+r} ${y} L ${x+r*.18} ${y+r*.18} L ${x} ${y+r} L ${x-r*.18} ${y+r*.18} L ${x-r} ${y} L ${x-r*.18} ${y-r*.18} Z`,
      {fill:color,opacity});
    const brightStars = [
      [43,62,4],[78,54,2.5],[119,73,3],[163,59,4.5],[216,57,2.5],[268,73,4],
      [38,115,3],[53,149,4],[38,188,2.5],[47,225,3],[37,271,4],[52,318,2.5],
      [282,112,3],[269,153,4],[282,197,2.5],[268,238,3.5],[282,280,2.5],[267,320,4],
      [39,354,3],[84,363,2.5],[124,375,3],[170,358,2.5],[221,373,4],[266,360,3]
    ];
    brightStars.forEach(([x,y,r],i) => {
      if(mode==='brain' && x>140 && y>88 && y<322) return;
      star(x,y,r,i%3===0?'#d1ad77':'#dfe8da',i%4===0?.95:.82);
    });
    const smallStars = [
      [59,83],[99,47],[136,54],[190,79],[237,87],[284,48],[33,93],[67,121],
      [39,162],[55,199],[31,243],[63,274],[42,300],[57,348],[90,345],[115,62],
      [256,51],[282,89],[257,132],[287,169],[258,198],[282,222],[255,273],[290,309],
      [248,345],[284,379],[201,359],[148,371],[103,382],[49,378]
    ];
    smallStars.forEach(([x,y],i) => {
      if(mode==='brain' && x>140 && y>88 && y<322) return;
      add(svg,'circle',{cx:x,cy:y,r:i%5===0?'1.4':'.85',fill:i%4===0?c.accent:'#dbe5d8',opacity:'.77'});
    });

    if (mode === 'eclipse') {
      const disc = add(svg,'g');
      add(disc,'circle',{cx:217,cy:167,r:77,fill:'#bda77e',opacity:'.25'});
      const eclipseClip=add(add(svg,'defs'),'clipPath',{id:'night-eclipse-disc'});
      add(eclipseClip,'circle',{cx:217,cy:167,r:77});
      const contours=add(disc,'g',{'clip-path':'url(#night-eclipse-disc)',fill:'none',stroke:'#e4d5aa','stroke-width':'.75',opacity:'.5'});
      for(const d of [
        'M 149 141 C 177 106 224 103 252 128 C 273 147 275 176 258 198',
        'M 151 154 C 182 123 219 120 244 142 C 263 160 260 183 244 201',
        'M 156 172 C 185 143 218 144 237 159 C 251 172 247 190 235 204',
        'M 164 189 C 192 166 215 167 228 179 C 239 189 231 205 218 215'
      ]) path(contours,d,{fill:'none'});
      add(disc,'circle',{cx:217,cy:167,r:77,fill:'none',stroke:'#dbc292','stroke-width':'1.1',opacity:'.9'});
    }
    if (mode === 'orbit') {
      add(svg,'ellipse',{cx:160,cy:211,rx:106,ry:145,transform:'rotate(-25 160 211)',fill:'none',stroke:'#d9bd89','stroke-width':'1.15',opacity:'.82'});
      add(svg,'ellipse',{cx:160,cy:211,rx:101,ry:140,transform:'rotate(-25 160 211)',fill:'none',stroke:'#809a91','stroke-width':'.6',opacity:'.65'});
      star(258,101,4.5,'#e5d1aa');
    }
    if (mode === 'comet') {
      path(svg,'M 257 151 C 270 123 280 103 291 81',{fill:'none',stroke:'#d1ad77','stroke-width':'1.45','stroke-linecap':'round',opacity:'.82'});
      path(svg,'M 254 152 C 264 128 271 110 278 96 M 260 151 C 272 130 281 117 289 108',{fill:'none',stroke:'#dfe8da','stroke-width':'.55','stroke-linecap':'round',opacity:'.66'});
      add(svg,'circle',{cx:257,cy:151,r:4.4,fill:'#e8d4a9'});
      add(svg,'circle',{cx:257,cy:151,r:7.5,fill:'none',stroke:'#e8d4a9','stroke-width':'.7',opacity:'.75'});
      star(278,96,2.6,'#e5d1aa',.87);
      star(290,108,2.2,'#dfe8da',.81);
    }
    if (mode === 'brain') {
      // An illustrative cerebral hemisphere and short stem: fixed constellation
      // nodes follow an intentional outline, with sparse edges suggesting folds.
      const outline = [
        [147,166],[153,145],[166,127],[184,119],[201,110],[221,116],
        [239,111],[256,129],[273,149],[279,169],[274,188],[282,209],
        [270,226],[268,241],[247,252],[225,246],[206,255],[184,249],
        [164,230],[150,202]
      ];
      const inner = [
        [174,157],[190,140],[210,134],[232,146],[252,160],
        [259,183],[242,199],[220,179],[201,166],[180,184],
        [171,209],[190,222],[211,235],[232,223],[253,227],
        [225,266],[217,280]
      ];
      const nodes=[...outline,...inner];
      const network=add(svg,'g',{fill:'none',stroke:'#b9cabb','stroke-linecap':'round'});
      const segment=(a,b,opacity,width='.68') => path(network,
        `M ${nodes[a][0]} ${nodes[a][1]} L ${nodes[b][0]} ${nodes[b][1]}`,
        {fill:'none','stroke-width':width,opacity});
      outline.forEach((_,i) => segment(i,(i+1)%outline.length,'.62','.85'));
      for(const [a,b] of [
        [0,20],[1,20],[2,21],[3,21],[4,22],[5,22],[5,23],[6,23],
        [7,24],[8,24],[8,25],[9,25],[10,26],[11,34],[12,34],
        [13,33],[14,32],[15,32],[16,31],[17,30],[18,30],[19,29],
        [20,21],[20,29],[21,22],[21,28],[22,23],[22,28],[23,24],
        [23,27],[24,25],[24,27],[25,26],[26,27],[26,34],[27,28],
        [27,31],[28,29],[28,31],[29,30],[30,31],[31,32],
        [32,33],[33,34],[14,35],[15,35],[35,36]
      ]) segment(a,b,'.37');
      for(const d of [
        'M 166 127 C 181 140 193 127 210 134 C 223 126 231 141 246 126',
        'M 174 157 C 189 145 198 174 211 159 C 227 148 239 176 252 160',
        'M 171 209 C 186 196 199 223 211 207 C 228 196 241 218 259 209'
      ]) path(network,d,{fill:'none',stroke:'#d9c28f','stroke-width':'.66',opacity:'.45'});
      nodes.forEach(([x,y],i) => {
        const major=i%4===0 || i===35 || i===36;
        add(svg,'circle',{cx:x,cy:y,r:major?'2.15':'1.35',fill:major?'#e6cb92':'#b9d0c1',opacity:major?'.96':'.82'});
        if(major && i!==36) star(x,y,3.1,'#e6cb92',.76);
      });
      path(svg,'M 145 179 C 140 175 135 176 129 181',{fill:'none',stroke:'#d2b27d','stroke-width':'.85',opacity:'.7'});
    }

    // The face alone floats in the center of the card. No skull, hair, or bust.
    const face=add(svg,'g',{transform:mode==='brain'?'translate(-5 27) scale(.95)':'translate(16 -39) scale(1.28)'});
    path(face,maskPath,{fill:stone,stroke:'#e5e9df','stroke-width':'2.1','stroke-linejoin':'round'});
    const faceClipId=`night-face-clip-${mode}`;
    const clip=add(add(face,'defs'),'clipPath',{id:faceClipId});
    path(clip,maskPath);
    const planes=add(face,'g',{'clip-path':`url(#${faceClipId})`});
    path(planes,'M 98 108 C 124 98 151 117 158 151 C 163 178 147 197 117 211 C 91 210 73 188 68 157 C 75 136 85 117 98 108 Z',{fill:light,opacity:'.65'});
    path(planes,'M 56 207 C 85 198 122 214 147 241 L 175 247 C 153 279 115 300 72 289 C 54 269 49 234 56 207 Z',{fill:'#9db5a6',opacity:'.53'});
    path(planes,'M 70 278 C 92 291 119 291 143 275 C 129 301 96 310 69 295 Z',{fill:light,opacity:'.58'});
    path(planes,'M 156 148 C 175 170 185 206 169 245 C 154 253 140 250 132 239 C 151 210 159 179 156 148 Z',{fill:'#739487',opacity:'.25'});
    if (mode === 'constellation') {
      const mapped = [[112,132],[141,143],[158,170],[120,188],[99,213],[137,219],[165,232]];
      path(planes,'M 112 132 L 141 143 L 158 170 M 141 143 L 120 188 L 99 213 M 120 188 L 137 219 L 165 232',{fill:'none',stroke:'#8b7554','stroke-width':'.8',opacity:'.76'});
      mapped.forEach(([x,y],i) => {
        add(planes,'circle',{cx:x,cy:y,r:i===1||i===3?'2.3':'1.65',fill:'#e9c987',stroke:'#7b694d','stroke-width':'.35'});
        if(i===1||i===3) path(planes,`M ${x} ${y-5} V ${y+5} M ${x-5} ${y} H ${x+5}`,{fill:'none',stroke:'#967d57','stroke-width':'.55',opacity:'.8'});
      });
    }
    path(face,'M 76 157 C 90 152 105 155 115 161',{fill:'none',stroke:ink,'stroke-width':'1.7','stroke-linecap':'round',opacity:'.74'});
    path(face,'M 80 176 Q 96 183 111 175',{fill:'none',stroke:ink,'stroke-width':'2.35','stroke-linecap':'round'});
    path(face,'M 63 240 Q 73 243 85 239',{fill:'none',stroke:ink,'stroke-width':'1.15','stroke-linecap':'round'});
    path(face,'M 107 226 C 129 237 148 246 169 245',{fill:'none',stroke:ink,'stroke-width':'1.05',opacity:'.32'});
    if (mode === 'orbit') {
      path(svg,'M 73 301 C 111 326 169 324 219 294 C 247 278 263 248 274 218',{fill:'none',stroke:'#e2c895','stroke-width':'1.4','stroke-linecap':'round',opacity:'.9'});
      add(svg,'circle',{cx:219,cy:294,r:2.5,fill:'#e2c895'});
    }
  }

  function drawSelectedNightOracle(svg, c) {
    const hairline = tracedHairline;
    const jaw = tracedJaw;
    const ink = '#304744';
    const stone = '#c8d4c7';
    const shadow = '#6f8d83';
    const light = '#e5e9df';

    const field = add(svg,'g',{fill:'#a9bfad',opacity:'.43'});
    for(let y=44;y<357;y+=9) for(let x=28;x<295;x+=9) {
      const radius=Math.hypot((x-166)*.94,y-183);
      if(radius>116 && radius<147) add(field,'circle',{cx:x,cy:y,r:'.82'});
    }
    add(svg,'circle',{cx:55,cy:89,r:27,fill:c.accent});
    add(svg,'circle',{cx:67,cy:77,r:26,fill:c.bg});
    for(const [x,y] of [[271,61],[291,107],[39,322],[277,324]]) add(svg,'circle',{cx:x,cy:y,r:'1.1',fill:'#dbe5d8'});

    const bust = add(svg,'g');
    path(bust,bustPath,{fill:stone,stroke:ink,'stroke-width':'1.5','stroke-linejoin':'round'});
    const clip=add(add(svg,'defs'),'clipPath',{id:'night-profile-clip'});
    path(clip,bustPath);
    const planes=add(bust,'g',{'clip-path':'url(#night-profile-clip)'});
    const hairCap = hairCapPath;
    path(planes,hairCap,{fill:shadow,opacity:'.57'});
    // Short, swept ridges give the crown a carved-hair reading without a helmet seam.
    path(planes,'M 111 101 C 127 77 145 66 165 65 C 182 64 195 70 207 79 C 188 72 173 74 160 82 C 141 91 131 105 122 120 Z',{fill:light,opacity:'.15'});
    path(planes,'M 136 68 C 154 65 170 69 185 78 C 196 86 205 96 211 108',{fill:'none',stroke:'#35574f','stroke-width':'1.6','stroke-linecap':'round',opacity:'.27'});
    path(planes,'M 172 58 C 196 63 215 75 230 93 C 239 104 245 116 249 130',{fill:'none',stroke:'#dce6d8','stroke-width':'1.5','stroke-linecap':'round',opacity:'.25'});
    path(planes,'M 214 76 C 236 89 252 107 259 129',{fill:'none',stroke:'#35574f','stroke-width':'1.4','stroke-linecap':'round',opacity:'.21'});
    path(planes,'M 98 119 C 119 105 139 115 151 137 C 160 162 153 187 127 207 C 101 209 75 191 69 158 C 79 137 88 124 98 119 Z',{fill:light,opacity:'.55'});
    path(planes,'M 219 121 C 258 147 272 192 260 234 C 254 250 247 261 237 270 C 221 247 212 215 207 189 C 202 163 208 141 219 121 Z',{fill:'#53776f',opacity:'.18'});
    path(planes,'M 57 213 C 83 203 121 217 143 247 L 158 267 C 134 292 106 302 72 289 C 59 269 53 239 57 213 Z',{fill:'#a4b7a8',opacity:'.44'});
    path(planes,'M 71 280 C 103 294 132 280 160 264 C 139 296 106 306 75 298 Z',{fill:light,opacity:'.56'});
    path(planes,'M 151 271 C 165 302 157 343 141 388 C 100 401 61 407 24 413 L 25 372 C 73 353 119 326 151 271 Z',{fill:'#66847a',opacity:'.58'});
    path(planes,'M 243 283 C 232 318 244 355 281 380 L 303 413 L 174 413 C 190 365 207 311 243 283 Z',{fill:light,opacity:'.67'});
    const dots=add(planes,'g',{fill:'#365b53',opacity:'.23'});
    for(let y=71;y<389;y+=8) for(let x=188;x<287;x+=8) if(Math.sin(x*.083+y*.039)>.26) add(dots,'circle',{cx:x,cy:y,r:'.75'});

    // The hairline stops at the temple; the crown is the outer edge of the hair.
    path(bust,smoothPath(hairline),{fill:'none',stroke:ink,'stroke-width':'1.15','stroke-linecap':'round',opacity:'.55'});
    path(bust,'M 76 157 C 90 152 105 155 115 161',{fill:'none',stroke:ink,'stroke-width':'2','stroke-linecap':'round',opacity:'.78'});
    path(bust,'M 80 176 Q 96 183 111 175',{fill:'none',stroke:ink,'stroke-width':'2.25','stroke-linecap':'round'});
    path(bust,'M 60.5 238 C 64 240 69 240 73 238.5',{fill:'none',stroke:ink,'stroke-width':'1.05','stroke-linecap':'round'});
    path(bust,'M 106 229 C 128 240 146 247 168 245',{fill:'none',stroke:ink,'stroke-width':'1.15',opacity:'.38'});
    path(bust,'M 152 272 C 155 304 153 350 139 380 M 242 287 C 226 313 224 345 239 372',{fill:'none',stroke:ink,'stroke-width':'1.2',opacity:'.48'});
    path(bust,'M 30 400 C 83 373 127 378 157 389 C 183 403 246 383 288 400',{fill:'none',stroke:ink,'stroke-width':'1.45',opacity:'.56'});
  }


  const makeCard = c => {
    const svg = el('svg', { viewBox:'0 0 320 420', 'aria-hidden':'true', focusable:'false' });
    add(svg, 'rect', { x:0, y:0, width:320, height:420, fill:c.bg });
    add(svg, 'rect', { x:13, y:13, width:294, height:394, fill:'none', stroke:c.border, 'stroke-width':'.8' });
    add(svg, 'path', { d:'M 24 37 H 296 M 24 384 H 296', fill:'none', stroke:c.border, 'stroke-width':'.7', opacity:'.72' });
    return svg;
  };

  // Minimal cards: the same traced profile as one flat form, one crescent, a few stars.
  // No frame rules, shading planes, or texture; volume comes from a single gradient.
  let minimalCount = 0;
  // Minimal cards keep the traced likeness from the brow ridge to the chin. The traced
  // forehead sloped ~35° and made the cranium read as a tilted dome, so everything above
  // the brow, plus the ear and neck, is constructed to adult proportions instead:
  // 1 cm ≈ 10.4 px from the glabella (69.5, 152); equal face thirds put the hairline near
  // y 90; head height ≈ 23.5 cm, depth ≈ 19.5 cm; the ear sits between brow and nose base.
  const smoothLoop = points => {
    const n = points.length;
    let d = `M ${points[0][0]} ${points[0][1]}`;
    for (let i = 0; i < n; i++) {
      const before = points[(i - 1 + n) % n], start = points[i];
      const end = points[(i + 1) % n], after = points[(i + 2) % n];
      const c1 = [start[0] + (end[0] - before[0]) / 6, start[1] + (end[1] - before[1]) / 6];
      const c2 = [end[0] - (after[0] - start[0]) / 6, end[1] - (after[1] - start[1]) / 6];
      d += ` C ${c1[0].toFixed(2)} ${c1[1].toFixed(2)} ${c2[0].toFixed(2)} ${c2[1].toFixed(2)} ${end[0]} ${end[1]}`;
    }
    return d + ' Z';
  };
  const continuePath = points => smoothPath(points).replace(/^M [^C]+/, '');
  const hairFront = [[138,34],[112,43],[96,57],[89,70],[87,83]];
  const forehead = [[86.5,92],[81.5,102],[76,116],[72.5,130],[70.5,142]];
  const faceTraced = tracedFront.slice(7);             // brow ridge → chin, from the photo
  const underChin = [[82.6,290.72],[103.6,292.76]];    // traced jaw landmarks under the chin
  const crown = [[234,232],[250,219],[265,203],[276,180],[281,152],[279,122],[268,90],[250,62],[224,42],[195,32],[165,30],[138,34]];
  const minimalHeadPath = smoothPath([...hairFront, ...forehead, ...faceTraced, ...underChin]) +
    ' C 112 294 116 298 118 306 C 121 322 124 340 128 354 C 131 366 108 376 80 384 C 52 391 22 395 0 398 L 0 420 L 320 420 L 320 384' +
    ' C 306 377 288 364 270 352 C 252 338 241 318 237 290 C 233 262 232 246 234 232' + continuePath(crown) + ' Z';
  // Short hair: frontal hairline, temple, a sideburn in front of the ear, an arc over it,
  // then a taper to the nape.
  const hairEdge = [[86.5,92],[104,99],[124,110],[146,126],[157,148],[160,176],[165,183],[169,166],[177,150],[192,143],[206,150],[212,170],[215,198],[224,218],[234,232]];
  const minimalHairPath = smoothPath(hairEdge) + continuePath(crown) + continuePath(hairFront) + ' L 86.5 92 Z';
  const earOutline = smoothLoop([[172,160],[184,148],[199,151],[207,166],[206,187],[199,205],[189,216],[179,216],[175,206],[173,190],[171,174]]);
  const earInner = smoothPath([[179,163],[192,156],[200,168],[198,186],[191,197]]);
  const earBowl = smoothPath([[184,180],[189,188],[185,196]]);
  // Interior jaw: from the throat up to the traced mandibular angle, below the ear.
  const jawLine = smoothPath([[110,293.6], ...tracedJaw.slice(2)]);
  const skinRim = smoothPath([...forehead, ...faceTraced, ...underChin]);
  const hairRim = smoothPath([...crown, ...hairFront.slice(1)]);
  const minimalThemes = {
    nocturne: {
      sky:['#13212d','#0b141c'], glow:'#26405a', face:['#f1ede2','#c9d1cb','#7e938d'], faceAxis:{ x1:60, y1:150, x2:250, y2:420 },
      hair:['#a3b4ae','#6f8580'], ink:'#25343b', moon:'#d8b57c', star:'#dfe7e1', fill:true, fade:false, earOpacity:.5
    },
    contour: {
      sky:['#13212d','#0b141c'], glow:'#1c3142', line:'#e7e2d4', ink:'#e7e2d4', moon:'#d8b57c', star:'#dfe7e1', fill:false, fade:true, earOpacity:.7, moreStars:true
    },
    // Contour dealt as a tarot card: an inner gold frame and a name plate under the bust.
    oracle: {
      sky:['#13212d','#0b141c'], glow:'#1c3142', line:'#e7e2d4', ink:'#e7e2d4', moon:'#d8b57c', star:'#dfe7e1', fill:false, fade:true, earOpacity:.7, moreStars:true,
      frame:'#d8b57c', title:'THE NIGHT ORACLE'
    },
    dusk: {
      // The sky runs N3 → Wake: the site's sleep-stage ramp, deepened for night.
      sky:['#111830','#29306a','#6b4f8f','#c46a6f','#e2a04f'], face:['#0d1222','#0d1222'], rim:'#f3c88a', backRim:'#a3adeb',
      ink:'#f3c88a', moon:'#f6e8cb', star:'#f1ece0', fill:true, fade:false, starsAbove:210, earOpacity:.38
    }
  };

  function drawMinimalOracle(svg, name) {
    const t = minimalThemes[name];
    const id = `oracle-${name}-${++minimalCount}`;
    const defs = add(svg, 'defs');
    const gradient = (gid, stops, attrs) => {
      const g = add(defs, 'linearGradient', { id:gid, gradientUnits:'userSpaceOnUse', ...attrs });
      stops.forEach((color, i) => add(g, 'stop', { offset:stops.length === 1 ? 0 : i / (stops.length - 1), 'stop-color':color }));
      return `url(#${gid})`;
    };

    add(svg, 'rect', { width:320, height:420, fill:gradient(`${id}-sky`, t.sky, { x1:0, y1:0, x2:0, y2:420 }) });
    if (t.glow) {
      const glow = add(defs, 'radialGradient', { id:`${id}-glow`, cx:178, cy:196, r:190, gradientUnits:'userSpaceOnUse' });
      add(glow, 'stop', { offset:0, 'stop-color':t.glow, 'stop-opacity':.95 });
      add(glow, 'stop', { offset:1, 'stop-color':t.glow, 'stop-opacity':0 });
      add(svg, 'rect', { width:320, height:420, fill:`url(#${id}-glow)` });
    }

    // Stars: a sparse, fixed constellation that stays clear of the head.
    for (const [x, y, r, o] of [[252,52,1.2,.9],[286,92,.8,.7],[214,34,.7,.55],[300,150,.7,.5],[34,276,.8,.55],[30,330,1,.7],[286,318,.9,.6],[124,30,.7,.5],[30,186,.8,.6]])
      if (y < (t.starsAbove || 420)) add(svg, 'circle', { cx:x, cy:y, r, fill:t.star, opacity:o });
    const sparkle = (x, y, r, color) => path(svg,
      `M ${x} ${y-r} Q ${x} ${y} ${x+r} ${y} Q ${x} ${y} ${x} ${y+r} Q ${x} ${y} ${x-r} ${y} Q ${x} ${y} ${x} ${y-r} Z`, { fill:color });
    sparkle(88, 40, 5, t.moon);
    sparkle(270, 70, 3, t.star);
    // A fuller sky for the line card: open sky only, clear of the head, moon, and shoulders.
    if (t.moreStars) {
      for (const [x, y, r, o] of [[20,24,.7,.5],[64,20,.9,.7],[160,14,.8,.6],[188,26,.6,.45],[236,18,1,.75],[296,30,.7,.55],
        [18,128,.7,.5],[24,226,1,.7],[16,250,.6,.45],[304,120,.9,.65],[292,200,.7,.5],[306,240,1.1,.7],[296,278,.6,.45],
        [52,330,.8,.6],[96,350,.6,.45],[20,368,.9,.6],[50,374,.6,.4]])
        add(svg, 'circle', { cx:x, cy:y, r, fill:t.star, opacity:o });
      sparkle(300, 212, 2.6, t.star);
      sparkle(24, 300, 2.4, t.moon);
    }

    // Crescent: a true cut-out (mask), so the sky gradient shows through.
    const moonMask = add(defs, 'mask', { id:`${id}-moon` });
    add(moonMask, 'rect', { width:320, height:420, fill:'#fff' });
    add(moonMask, 'circle', { cx:61, cy:76, r:19, fill:'#000' });
    add(svg, 'circle', { cx:50, cy:85, r:20, fill:t.moon, mask:`url(#${id}-moon)` });

    // The bust dissolves into the sky instead of ending on drape lines.
    let host = svg;
    if (t.fade) {
      const fade = add(defs, 'mask', { id:`${id}-fade`, maskUnits:'userSpaceOnUse', x:0, y:0, width:320, height:420 });
      // Eased falloff: holds through the neck, then dissolves across the shoulders.
      add(fade, 'rect', { width:320, height:420, fill:gradient(`${id}-fadeg`, ['#fff', '#fff', '#b3b3b3', '#4d4d4d', '#141414', '#000'], { x1:0, y1:260, x2:0, y2:410 }) });
      host = add(svg, 'g', { mask:`url(#${id}-fade)` });
    }
    // The head sits a little lower than the traced coordinates to give the crown headroom.
    const fig = add(host, 'g', { transform:'translate(0 14)' });
    const stroke = (d, color, width, opacity) => path(fig, d,
      { fill:'none', stroke:color, 'stroke-width':width, 'stroke-linecap':'round', 'stroke-linejoin':'round', opacity });
    const clipId = `${id}-clip`;
    path(add(defs, 'clipPath', { id:clipId }), minimalHeadPath);
    if (t.fill) {
      path(fig, minimalHeadPath, { fill:gradient(`${id}-face`, t.face, t.faceAxis || { x1:50, y1:160, x2:290, y2:250 }) });
      if (t.hair) path(add(fig, 'g', { 'clip-path':`url(#${clipId})` }), minimalHairPath,
        { fill:gradient(`${id}-hair`, t.hair, { x1:110, y1:40, x2:280, y2:250 }) });
      if (t.rim) {
        // Warm light on the skin only, tapering off under the chin where the throat begins.
        const taper = add(defs, 'linearGradient', { id:`${id}-rim`, gradientUnits:'userSpaceOnUse', x1:82, y1:0, x2:106, y2:0 });
        add(taper, 'stop', { offset:0, 'stop-color':t.rim });
        add(taper, 'stop', { offset:1, 'stop-color':t.rim, 'stop-opacity':0 });
        stroke(skinRim, `url(#${id}-rim)`, 1.4, .92);
      }
      // Faint cool rim on the hair so the head separates from the night sky; fades at the nape.
      if (t.backRim) stroke(hairRim, gradient(`${id}-back`, ['#0d1222', t.backRim, t.backRim], { x1:0, y1:236, x2:0, y2:60 }), 1.2, .6);
    } else {
      path(fig, minimalHeadPath, { fill:'none', stroke:t.line, 'stroke-width':1.6, 'stroke-linejoin':'round' });
      stroke(smoothPath(hairEdge), t.line, 1, .35);
    }

    if (t.frame) {
      add(svg, 'rect', { x:12.5, y:12.5, width:295, height:395, rx:8, fill:'none', stroke:t.frame, 'stroke-width':.8, opacity:.42 });
    }
    if (t.title) {
      // The fade leaves the foot of the card empty: a classic tarot name plate.
      add(svg, 'path', { d:'M 58 383.5 H 94 M 226 383.5 H 262', stroke:t.frame, 'stroke-width':.6, opacity:.5 });
      const label = add(svg, 'text', { x:160, y:387, 'text-anchor':'middle', fill:t.frame, 'font-size':7.4, 'letter-spacing':2.6,
        'font-family':"Charter,'Iowan Old Style',Georgia,serif", opacity:.92 });
      label.textContent = t.title;
    }

    // Features: brow, closed eye, lips, jaw, and a simple ear.
    stroke('M 77 157 C 90 152.5 104 155 114 160.5', t.ink, 1.5, .5);
    stroke('M 81 176 Q 96 182.5 110 175.5', t.ink, 2.1, .95);
    stroke('M 61 238 C 64.5 240 69 240 72.5 238.5', t.ink, 1.1, .8);
    stroke(jawLine, t.ink, 1.1, t.fill ? .3 : .45);
    stroke(earOutline, t.ink, 1.2, t.earOpacity);
    stroke(earInner, t.ink, 1, t.earOpacity * .75);
    stroke(earBowl, t.ink, 1, t.earOpacity * .6);
  }

  const makeMinimalCard = name => {
    const svg = el('svg', { viewBox:'0 0 320 420', 'aria-hidden':'true', focusable:'false' });
    drawMinimalOracle(svg, name);
    return svg;
  };

  document.querySelectorAll('[data-minimal-study]').forEach(host => {
    host.replaceChildren(makeMinimalCard(host.dataset.minimalStudy));
  });

  document.querySelectorAll('[data-head-study]').forEach(host => {
    const variant = Number(host.dataset.headStudy);
    const c = colors[variant - 1];
    const shape = portrait;
    const svg = makeCard(c);

    if (variant === 2) {
      drawSelectedNightOracle(svg,c);
      add(svg,'circle',{cx:160,cy:25,r:2.2,fill:c.accent});
      host.replaceChildren(svg);
      return;
    }

    const defs = add(svg, 'defs');
    const id = `head-clip-${variant}`;
    const clip = add(defs, 'clipPath', { id });
    path(clip, shape);
    const maskId = `arch-clip-${variant}`;
    const arch = add(defs, 'clipPath', { id:maskId });
    path(arch, 'M 44 304 L 44 168 C 44 85 102 39 169 39 C 241 39 287 94 287 168 L 287 304 Z');

    if (variant === 1) {
      add(svg, 'circle', { cx:165, cy:171, r:112, fill:'none', stroke:c.accent, 'stroke-width':'1.2', opacity:'.72' });
      add(svg, 'circle', { cx:165, cy:171, r:124, fill:'none', stroke:c.mist, 'stroke-width':'.7' });
    } else if (variant === 3) {
      add(svg, 'circle', { cx:165, cy:174, r:121, fill:'none', stroke:c.border, 'stroke-width':'.8' });
      add(svg, 'circle', { cx:165, cy:174, r:105, fill:'none', stroke:c.border, 'stroke-width':'.7', 'stroke-dasharray':'1 5' });
    } else {
      path(svg, 'M 52 303 V 166 A 108 108 0 0 1 268 166 V 303', { fill:'none', stroke:c.accent, 'stroke-width':'1.3', opacity:'.8' });
      path(svg, 'M 41 305 V 166 A 119 119 0 0 1 279 166 V 305', { fill:'none', stroke:c.mist, 'stroke-width':'.8' });
    }

    // Transform the bust for two poses while keeping the card framing fixed.
    const figure = add(svg, 'g', variant === 3 ? { transform:'translate(23 20) scale(.86) rotate(12 166 204)' } : {});
    path(figure, shape, { fill:c.fill });
    const shade = add(figure, 'g', { 'clip-path':`url(#${id})` });
    path(shade, 'M 35 90 C 89 84 136 118 148 171 C 158 212 133 261 82 301 L 22 329 Z', { fill:c.shade, opacity:'.16' });
    path(shade, 'M 121 283 C 158 311 160 357 139 414 L 26 414 L 37 359 Z', { fill:c.shade, opacity:'.1' });

    const dots = add(figure, 'g', { 'clip-path':`url(#${id})`, fill:c.dots });
    for (let y=60; y<400; y+=7) for (let x=39; x<287; x+=7) {
      const nearFace = x>178 && y<297;
      const marble = Math.sin(x*.073 + y*.041) + Math.cos(x*.036 - y*.052);
      if (marble > (nearFace ? .5 : .05)) add(dots,'circle',{cx:x,cy:y,r:nearFace ? .95 : 1.2,opacity:nearFace ? '.62' : '.7'});
    }
    path(figure, hair, { fill:c.ink, opacity:variant === 4 ? '.1' : '.17' });
    path(figure, hairline, { fill:'none', stroke:c.ink, 'stroke-width':'1.2', opacity:'.82' });
    path(figure, shape, { fill:'none', stroke:c.ink, 'stroke-width':'1.35', 'stroke-linejoin':'round' });
    const details = [[eye,2.6,1],[brow,1.1,.55],[lips,1.1,.7],[neck1,1.15,.44],[neck2,1,.35],[drape,1.2,.53]];
    for (const [d,w,opacity] of details) path(figure,d,{fill:'none',stroke:c.ink,'stroke-width':w,'stroke-linecap':'round',opacity});
    if (variant === 4) {
      for (const d of [
        'M 64 154 C 83 100 122 77 169 75 C 208 74 235 92 251 119',
        'M 71 162 C 94 111 127 91 171 89 C 201 88 227 102 245 125',
        'M 82 164 C 105 128 137 105 171 104 C 201 104 222 113 237 130'
      ]) path(figure,d,{fill:'none',stroke:c.accent,'stroke-width':'1.1',opacity:'.68'});
    }
    if (variant === 3 || variant === 4) {
      const field = add(svg,'g',{ 'clip-path':`url(#${maskId})`, fill:c.accent, opacity:variant === 3 ? '.48' : '.34' });
      for(let y=48;y<350;y+=10) for(let x=36;x<300;x+=10) {
        const r=Math.hypot(x-165,y-173);
        if(r>112 && r<142) add(field,'circle',{cx:x,cy:y,r:1.25});
      }
    }
    add(svg,'circle',{cx:160,cy:25,r:2.2,fill:c.accent});
    host.replaceChildren(svg);
  });

  document.querySelectorAll('[data-celestial-study]').forEach(host => {
    const svg=makeCard(colors[1]);
    drawNightOracle(svg,colors[1],host.dataset.celestialStudy);
    path(svg,'M 160 21 L 160.7 24.3 L 164 25 L 160.7 25.7 L 160 29 L 159.3 25.7 L 156 25 L 159.3 24.3 Z',{fill:colors[1].accent});
    host.replaceChildren(svg);
  });

  // data-selected-portrait="dusk" (or nocturne, contour) picks a minimal card;
  // an empty value keeps the original framed Night Oracle.
  document.querySelectorAll('[data-selected-portrait]').forEach(host => {
    const theme = host.dataset.selectedPortrait;
    if (minimalThemes[theme]) {
      host.replaceChildren(makeMinimalCard(theme));
      return;
    }
    const svg=makeCard(colors[1]);
    drawSelectedNightOracle(svg,colors[1]);
    add(svg,'circle',{cx:160,cy:25,r:2.2,fill:colors[1].accent});
    host.replaceChildren(svg);
  });
})();
