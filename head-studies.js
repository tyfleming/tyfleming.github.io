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
    // Side-profile landmarks follow the supplied reference: broad posterior skull,
    // prominent brow and nose, compact face, square chin, and a clear jaw angle.
    const bustPath = 'M 182 71 C 144 66 117 82 108 117 C 101 135 99 153 82 167 C 76 173 75 180 84 184 C 88 189 85 197 76 208 L 56 220 C 49 225 50 232 59 234 C 63 236 67 234 70 237 L 68 249 C 74 252 78 251 78 256 C 79 261 73 264 70 270 C 66 280 69 292 77 298 C 87 303 101 303 112 301 C 130 297 145 285 153 276 C 151 309 160 333 178 348 C 209 366 255 371 287 389 L 290 407 L 28 407 L 30 391 C 66 370 103 362 131 346 C 147 333 150 315 146 305 C 184 297 207 289 230 275 C 249 261 263 236 268 207 C 277 165 268 117 237 88 C 220 75 201 70 182 71 Z';
    const ink = '#304744';
    const stone = '#c8d4c7';
    const shadow = '#6f8d83';
    const light = '#e5e9df';

    const field = add(svg,'g',{fill:'#a9bfad',opacity:'.43'});
    for(let y=46;y<358;y+=9) for(let x=30;x<295;x+=9) {
      const radius=Math.hypot((x-168)*.91,y-188);
      if(radius>119 && radius<148) add(field,'circle',{cx:x,cy:y,r:'.82'});
    }
    add(svg,'circle',{cx:60,cy:86,r:27,fill:c.accent});
    add(svg,'circle',{cx:71,cy:75,r:26,fill:c.bg});
    for(const [x,y] of [[271,61],[291,107],[47,319],[277,324]]) add(svg,'circle',{cx:x,cy:y,r:'1.1',fill:'#dbe5d8'});

    const bust = add(svg,'g',{transform:'translate(18 40) scale(.9 .9)'});
    path(bust,bustPath,{fill:stone,stroke:ink,'stroke-width':'1.55','stroke-linejoin':'round'});
    const clip=add(add(svg,'defs'),'clipPath',{id:'night-profile-clip'});
    path(clip,bustPath);
    const planes=add(bust,'g',{'clip-path':'url(#night-profile-clip)'});

    // Broad rear cranial mass and planar cheekbone borrow the reference's proportions.
    path(planes,'M 168 65 C 226 53 293 101 305 155 C 316 218 274 273 230 293 C 205 273 196 240 211 202 C 222 157 210 107 168 65 Z',{fill:shadow,opacity:'.54'});
    path(planes,'M 107 115 C 130 94 158 99 180 114 C 183 145 167 177 148 189 C 135 205 131 226 136 248 C 114 263 93 254 76 240 C 107 204 95 158 107 115 Z',{fill:light,opacity:'.75'});
    path(planes,'M 99 182 C 116 178 129 185 135 195 C 137 208 126 218 115 224 C 102 218 98 200 99 182 Z',{fill:'#a8bcae',opacity:'.31'});
    path(planes,'M 86 231 C 112 230 139 241 157 259 L 165 279 C 149 294 131 302 112 300 L 72 280 Z',{fill:'#9cafa2',opacity:'.42'});
    path(planes,'M 87 290 C 113 299 134 292 155 280 C 141 301 120 307 99 303 C 92 299 89 295 87 290 Z',{fill:light,opacity:'.53'});
    path(planes,'M 145 300 C 168 320 164 354 150 382 C 112 395 71 403 27 411 L 25 378 C 86 353 125 339 145 300 Z',{fill:'#66847a',opacity:'.58'});
    path(planes,'M 246 276 C 239 315 244 352 281 380 L 303 411 L 179 411 C 186 365 208 310 246 276 Z',{fill:light,opacity:'.7'});
    const dots=add(planes,'g',{fill:'#365b53',opacity:'.27'});
    for(let y=89;y<389;y+=8) for(let x=181;x<287;x+=8) if(Math.sin(x*.083+y*.039)>.26) add(dots,'circle',{cx:x,cy:y,r:'.75'});

    // Ear intentionally omitted. Facial details stay aligned to the traced profile.
    path(bust,'M 99 180 C 112 174 126 176 139 184',{fill:'none',stroke:ink,'stroke-width':'2.2','stroke-linecap':'round',opacity:'.8'});
    path(bust,'M 102 198 Q 116 204 130 197',{fill:'none',stroke:ink,'stroke-width':'2.4','stroke-linecap':'round'});
    path(bust,'M 69 252 Q 76 253 82 251 M 69 267 Q 77 268 82 265',{fill:'none',stroke:ink,'stroke-width':'1.1','stroke-linecap':'round'});
    path(bust,'M 93 273 C 107 290 129 295 147 281 M 148 280 C 163 275 176 266 186 255',{fill:'none',stroke:ink,'stroke-width':'1.2',opacity:'.4'});
    path(bust,'M 149 307 C 170 324 170 353 160 378 M 245 283 C 230 309 227 342 242 370',{fill:'none',stroke:ink,'stroke-width':'1.25',opacity:'.53'});
    path(bust,'M 33 399 C 83 374 123 376 153 389 C 183 403 240 384 286 400',{fill:'none',stroke:ink,'stroke-width':'1.5',opacity:'.58'});
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
