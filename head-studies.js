// Four deterministic vector studies. No raster assets, external libraries, or animation.
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

  function drawNightOracle(svg, c) {
    // Measured from the supplied photo by scripts/trace_profile.py.
    // The front contour is extracted from pixels; only the rear skull and bust are drawn by hand.
    const tracedFront = [
      [132.04,56.8],[125.52,62.92],[101.28,104.4],[87.72,120.04],
      [81.38,137.04],[75.86,141.8],[73.98,147.24],[69.82,152],
      [69.34,157.44],[75.38,167.64],[74.68,171.04],[59.59,184.64],
      [45.02,201.64],[44.1,209.12],[45.54,212.52],[57.09,217.28],
      [59.98,220.68],[58.84,237],[61.51,242.44],[59.54,249.24],
      [65.76,258.08],[61.64,262.84],[59.54,276.44],[60.94,279.84],
      [69.74,288]
    ];
    // Two interpreted landmarks from the same source photograph. The hairline
    // ends at the temple; the crown above it is the outer edge of the hair.
    const hairline = [
      [102.2,109.84],[112.7,104.4],[124.6,101.68],[135.8,105.76],
      [147.7,115.96],[154,129.56],[163.1,143.16],[173.6,157.44]
    ];
    const jaw = [
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
    const bustPath = smoothPath([...tracedFront, ...jaw]) +
      ' C 166 272 164 308 163 330 C 131 352 78 372 27 390 L 27 407 L 294 407 L 290 389 C 267 377 247 359 241 333 C 238 317 239 301 245 284 C 268 264 282 232 287 196 C 293 148 274 101 235 72 C 208 52 167 43 132.04 56.8 Z';
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
    const hairCap = 'M 102.2 109.84 C 112 78 125 57 132.04 56.8 C 167 43 208 52 235 72 C 274 101 293 148 287 196 C 282 232 268 264 245 284 C 218 260 213 223 208 202 C 201 181 187 166 173.6 157.44 ' +
      smoothPath([...hairline].reverse()).replace(/^M [^C]+/, '') + ' Z';
    path(planes,hairCap,{fill:shadow,opacity:'.57'});
    path(planes,'M 98 119 C 119 105 139 115 151 137 C 160 162 153 187 127 207 C 101 209 75 191 69 158 C 79 137 88 124 98 119 Z',{fill:light,opacity:'.55'});
    path(planes,'M 219 121 C 258 147 272 192 260 234 C 254 250 247 261 237 270 C 221 247 212 215 207 189 C 202 163 208 141 219 121 Z',{fill:'#53776f',opacity:'.18'});
    path(planes,'M 57 213 C 83 203 121 217 143 247 L 158 267 C 134 292 106 302 72 289 C 59 269 53 239 57 213 Z',{fill:'#a4b7a8',opacity:'.44'});
    path(planes,'M 71 280 C 103 294 132 280 160 264 C 139 296 106 306 75 298 Z',{fill:light,opacity:'.56'});
    path(planes,'M 155 279 C 180 305 178 345 157 388 C 110 402 70 407 24 413 L 25 372 C 91 350 128 329 155 279 Z',{fill:'#66847a',opacity:'.58'});
    path(planes,'M 243 283 C 232 318 244 355 281 380 L 303 413 L 174 413 C 190 365 207 311 243 283 Z',{fill:light,opacity:'.67'});
    const dots=add(planes,'g',{fill:'#365b53',opacity:'.23'});
    for(let y=71;y<389;y+=8) for(let x=188;x<287;x+=8) if(Math.sin(x*.083+y*.039)>.26) add(dots,'circle',{cx:x,cy:y,r:'.75'});

    // The ear and hair detail remain absent; the hairline stops at the temple.
    path(bust,smoothPath(hairline),{fill:'none',stroke:ink,'stroke-width':'1.15','stroke-linecap':'round',opacity:'.55'});
    path(bust,'M 76 157 C 90 152 105 155 115 161',{fill:'none',stroke:ink,'stroke-width':'2','stroke-linecap':'round',opacity:'.78'});
    path(bust,'M 80 176 Q 96 183 111 175',{fill:'none',stroke:ink,'stroke-width':'2.25','stroke-linecap':'round'});
    path(bust,'M 63 240 Q 73 243 85 239',{fill:'none',stroke:ink,'stroke-width':'1.1','stroke-linecap':'round'});
    path(bust,'M 106 229 C 128 240 146 247 168 245',{fill:'none',stroke:ink,'stroke-width':'1.15',opacity:'.38'});
    path(bust,'M 167 273 C 175 307 174 352 161 380 M 242 287 C 226 313 224 345 239 372',{fill:'none',stroke:ink,'stroke-width':'1.2',opacity:'.48'});
    path(bust,'M 30 400 C 83 373 127 378 157 389 C 183 403 246 383 288 400',{fill:'none',stroke:ink,'stroke-width':'1.45',opacity:'.56'});
  }

  document.querySelectorAll('[data-head-study]').forEach(host => {
    const variant = Number(host.dataset.headStudy);
    const c = colors[variant - 1];
    const shape = portrait;
    const svg = el('svg', { viewBox:'0 0 320 420', 'aria-hidden':'true', focusable:'false' });
    add(svg, 'rect', { x:0, y:0, width:320, height:420, fill:c.bg });
    add(svg, 'rect', { x:13, y:13, width:294, height:394, fill:'none', stroke:c.border, 'stroke-width':'.8' });
    add(svg, 'path', { d:'M 24 37 H 296 M 24 384 H 296', fill:'none', stroke:c.border, 'stroke-width':'.7', opacity:'.72' });

    if (variant === 2) {
      drawNightOracle(svg,c);
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
    add(figure,'circle',{cx:238,cy:201,r:1.2,fill:c.ink});

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
})();
