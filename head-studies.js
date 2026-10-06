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
    // A side-view classical bust. The brow, nose, lips, chin, and jaw are one continuous silhouette.
    const bustPath = 'M 150 85 C 110 87 83 116 76 158 C 70 197 78 238 98 266 C 110 284 124 296 139 307 L 136 329 C 132 352 91 363 36 386 L 29 407 L 289 407 L 283 387 C 251 375 224 363 209 347 C 202 338 202 328 206 322 C 217 320 224 323 233 323 L 244 318 C 253 313 255 304 254 295 L 254 285 C 258 279 257 276 251 272 L 245 269 C 254 264 257 260 252 255 L 249 252 C 270 250 279 244 275 237 C 272 230 263 226 257 219 C 244 205 238 187 237 172 C 234 126 194 87 150 85 Z';
    const ink = '#2e4543';
    const stone = '#c6d2c5';
    const shadow = '#6d8980';
    const light = '#e1e8de';

    const field = add(svg,'g',{fill:'#acc0b0',opacity:'.44'});
    for(let y=54;y<357;y+=9) for(let x=31;x<291;x+=9) {
      const radius=Math.hypot((x-161)*.93,y-193);
      if(radius>116 && radius<148) add(field,'circle',{cx:x,cy:y,r:'.85'});
    }
    add(svg,'circle',{cx:62,cy:93,r:28,fill:c.accent});
    add(svg,'circle',{cx:74,cy:81,r:27,fill:c.bg});
    for(const [x,y] of [[262,70],[284,169],[44,267],[267,317]]) add(svg,'circle',{cx:x,cy:y,r:'1.1',fill:'#dbe5d8'});

    const bust = add(svg,'g',{transform:'translate(7 9) scale(.96)'});
    path(bust,bustPath,{fill:stone,stroke:ink,'stroke-width':'1.55','stroke-linejoin':'round'});
    const clip=add(add(svg,'defs'),'clipPath',{id:'night-profile-clip'});
    path(clip,bustPath);
    const planes=add(bust,'g',{'clip-path':'url(#night-profile-clip)'});

    // Flat tonal planes give the marble form depth without a bitmap or gradient.
    path(planes,'M 69 77 C 122 88 139 136 133 177 C 118 212 106 247 129 301 C 139 330 131 365 113 410 L 18 410 L 15 86 Z',{fill:shadow,opacity:'.78'});
    path(planes,'M 174 95 C 205 105 229 132 237 171 L 238 215 C 227 224 219 235 207 248 C 192 259 173 259 157 252 C 155 213 166 178 171 142 Z',{fill:light,opacity:'.75'});
    path(planes,'M 217 188 C 228 202 240 224 275 238 L 270 254 C 254 255 242 251 231 240 Z',{fill:'#eef0e9',opacity:'.7'});
    path(planes,'M 151 246 C 174 242 190 255 207 273 C 222 293 236 293 256 284 C 249 310 226 325 199 326 C 171 324 148 307 139 280 Z',{fill:'#a5b7a9',opacity:'.8'});
    path(planes,'M 186 296 C 206 302 226 301 250 292 C 237 318 219 328 197 328 C 183 319 179 310 186 296 Z',{fill:light,opacity:'.7'});
    path(planes,'M 136 306 C 161 324 161 347 149 382 C 131 390 95 393 31 410 L 18 410 L 18 362 Z',{fill:'#536f69',opacity:'.5'});
    path(planes,'M 206 322 C 198 352 222 370 257 384 L 297 410 L 168 410 C 173 377 187 345 206 322 Z',{fill:light,opacity:'.8'});
    const dots=add(planes,'g',{fill:'#41635b',opacity:'.28'});
    for(let y=120;y<383;y+=8) for(let x=78;x<147;x+=8) if(Math.sin(x*.079+y*.047)>.18) add(dots,'circle',{cx:x,cy:y,r:'.85'});

    // Ear, closed eye, nose plane, mouth, and carved neck lines stay understated.
    path(bust,'M 111 211 C 103 199 96 206 98 225 C 100 244 110 250 119 238 C 126 227 122 216 111 211 Z',{fill:'#9fb3a5',stroke:ink,'stroke-width':'1.25'});
    path(bust,'M 106 218 C 115 215 118 229 111 236',{fill:'none',stroke:ink,'stroke-width':'1.05','stroke-linecap':'round'});
    path(bust,'M 198 188 Q 215 180 231 188',{fill:'none',stroke:ink,'stroke-width':'1.6','stroke-linecap':'round',opacity:'.7'});
    path(bust,'M 202 202 Q 217 211 231 202',{fill:'none',stroke:ink,'stroke-width':'2.7','stroke-linecap':'round'});
    path(bust,'M 231 185 C 239 207 249 222 268 237',{fill:'none',stroke:ink,'stroke-width':'1.05',opacity:'.45'});
    path(bust,'M 237 257 Q 245 260 251 255 M 234 276 Q 245 276 251 274',{fill:'none',stroke:ink,'stroke-width':'1.25','stroke-linecap':'round'});
    path(bust,'M 158 282 C 177 305 199 313 219 308',{fill:'none',stroke:ink,'stroke-width':'1.3',opacity:'.46'});
    path(bust,'M 142 314 C 162 339 159 368 150 389 M 204 325 C 182 346 180 375 183 397',{fill:'none',stroke:ink,'stroke-width':'1.25',opacity:'.55'});
    path(bust,'M 38 399 C 93 373 134 375 159 389 C 184 403 244 385 284 400',{fill:'none',stroke:ink,'stroke-width':'1.5',opacity:'.6'});
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
