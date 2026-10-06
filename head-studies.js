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
    const face = 'M 106 158 C 125 134 156 130 187 143 C 225 148 248 179 247 211 L 242 237 C 242 246 252 252 254 261 C 254 270 244 274 233 277 C 226 295 217 309 199 318 C 180 327 152 318 133 306 C 111 292 96 270 93 242 C 87 211 92 179 106 158 Z';
    const neck = 'M 130 295 C 136 321 126 345 108 361 C 87 373 58 376 30 391 L 25 408 L 294 408 L 288 386 C 260 374 225 359 208 337 C 201 326 202 312 205 302 Z';
    const hairMass = 'M 81 189 C 66 165 73 122 104 95 C 131 71 176 69 209 83 C 246 94 267 128 257 164 C 250 183 228 187 209 175 C 189 164 174 162 151 172 C 118 190 100 203 81 189 Z';
    const ink = '#2c4141';
    const mid = '#8d9f96';
    const light = '#d7dfd5';
    const shadow = '#526d69';

    // A sparse, measured halo keeps the point-grid idea outside the face.
    const halo = add(svg, 'g', { fill:'#a9c0ae', opacity:'.42' });
    for (let y=57; y<357; y+=9) for (let x=34; x<292; x+=9) {
      const distance = Math.hypot((x-160)*.92, y-191);
      if (distance>112 && distance<145) add(halo,'circle',{cx:x,cy:y,r:'.85'});
    }
    add(svg,'circle',{cx:274,cy:91,r:31,fill:c.accent,opacity:'.95'});
    add(svg,'circle',{cx:288,cy:78,r:29,fill:c.bg});
    for (const [x,y,r] of [[52,87,1.3],[88,64,1],[265,174,1],[281,273,1.1],[46,321,.9]]) add(svg,'circle',{cx:x,cy:y,r,fill:'#d8e3d6'});

    const bust = add(svg,'g',{transform:'translate(15 35) scale(.91)'});
    path(bust,neck,{fill:'#b9c9bd',stroke:ink,'stroke-width':'1.5'});
    path(bust,'M 128 300 C 151 326 143 352 133 377 C 109 386 78 388 43 407 L 25 408 L 30 391 C 74 366 113 353 128 300 Z',{fill:shadow,opacity:'.72'});
    path(bust,'M 200 310 C 190 340 201 363 222 377 C 246 384 270 391 294 408 L 183 408 C 170 386 170 357 182 329 Z',{fill:light,opacity:'.9'});
    path(bust,'M 39 404 C 90 375 128 377 156 390 C 188 408 246 390 288 400',{fill:'none',stroke:ink,'stroke-width':'1.7',opacity:'.72'});
    path(bust,'M 130 346 C 147 367 157 377 171 382 M 202 338 C 211 358 229 369 254 379',{fill:'none',stroke:ink,'stroke-width':'1.3',opacity:'.45'});

    path(bust,hairMass,{fill:'#71857f',stroke:ink,'stroke-width':'1.5'});
    path(bust,face,{fill:'#c8d5c9',stroke:ink,'stroke-width':'1.5'});
    const faceClip = add(add(svg,'defs'),'clipPath',{id:'night-face-clip'});
    path(faceClip,face);
    const facets = add(bust,'g',{'clip-path':'url(#night-face-clip)'});
    path(facets,'M 102 147 C 124 171 119 195 111 226 C 102 262 126 302 151 317 L 76 320 L 77 149 Z',{fill:'#7d968d'});
    path(facets,'M 151 163 C 168 155 186 160 202 177 C 197 192 191 207 187 222 C 173 226 157 223 145 211 C 137 192 141 174 151 163 Z',{fill:'#e1e7dd',opacity:'.85'});
    path(facets,'M 190 221 C 206 223 217 228 230 241 L 238 258 C 224 266 210 262 196 255 Z',{fill:'#91a69d'});
    path(facets,'M 119 254 C 144 243 164 253 178 273 C 180 290 172 304 157 311 C 133 298 117 279 119 254 Z',{fill:'#b2c3b5'});
    path(facets,'M 166 294 C 190 286 205 287 223 279 C 218 303 205 318 185 324 C 171 319 166 307 166 294 Z',{fill:'#e6ebe2',opacity:'.75'});
    const stipple = add(facets,'g',{fill:shadow,opacity:'.34'});
    for(let y=158;y<318;y+=8) for(let x=94;x<155;x+=8) if(Math.sin(x*.075+y*.041)>.05) add(stipple,'circle',{cx:x,cy:y,r:'.85'});

    // Two closed lids and planar nose, lips, cheek, and jaw give the bowed face its expression.
    path(bust,'M 123 215 C 138 207 151 208 165 216 M 188 213 C 200 205 216 207 226 215',{fill:'none',stroke:ink,'stroke-width':'2.1','stroke-linecap':'round',opacity:'.56'});
    path(bust,'M 126 226 Q 145 238 161 228 M 190 226 Q 208 237 222 226',{fill:'none',stroke:ink,'stroke-width':'2.7','stroke-linecap':'round'});
    path(bust,'M 207 218 C 214 233 223 245 241 258 C 249 266 239 271 225 270 C 219 270 213 267 210 263',{fill:'none',stroke:ink,'stroke-width':'1.7','stroke-linecap':'round'});
    path(bust,'M 211 275 C 220 274 226 277 231 281 M 204 286 Q 217 292 229 285',{fill:'none',stroke:ink,'stroke-width':'1.55','stroke-linecap':'round'});
    path(bust,'M 107 212 C 98 200 90 207 93 225 C 96 243 107 247 114 237 M 100 217 C 108 214 110 226 105 232',{fill:'none',stroke:ink,'stroke-width':'1.35','stroke-linecap':'round'});
    path(bust,'M 120 264 C 136 284 152 294 170 299 M 176 306 C 191 309 206 303 217 293',{fill:'none',stroke:ink,'stroke-width':'1.2',opacity:'.42'});

    // Raised locks echo carved Greek marble rather than a smooth cartoon hair cap.
    const curls = [
      ['M 84 154 C 83 126 102 100 124 97 C 144 93 148 112 136 124 C 124 139 107 133 109 117',16],
      ['M 126 107 C 131 79 158 79 172 93 C 186 108 167 131 151 124 C 140 119 146 105 157 105',17],
      ['M 173 95 C 185 79 211 85 219 103 C 226 120 207 132 194 121 C 188 115 194 106 202 108',17],
      ['M 218 112 C 237 102 253 119 250 138 C 248 154 230 162 217 151 C 210 144 218 132 228 137',16],
      ['M 84 158 C 68 172 76 193 92 196 C 107 199 119 187 112 175',14],
      ['M 117 147 C 132 128 151 138 150 154 C 149 173 125 179 117 165',16],
      ['M 157 141 C 176 124 194 139 189 157 C 185 173 165 175 158 159',16],
      ['M 196 147 C 212 136 227 151 220 166 C 215 177 201 179 193 168',15]
    ];
    for(const [d,width] of curls) {
      path(bust,d,{fill:'none',stroke:'#4d655f','stroke-width':width+3,'stroke-linecap':'round','stroke-linejoin':'round'});
      path(bust,d,{fill:'none',stroke:'#dce5da','stroke-width':width,'stroke-linecap':'round','stroke-linejoin':'round'});
      path(bust,d,{fill:'none',stroke:'#f0f1e9','stroke-width':'2.1','stroke-linecap':'round',opacity:'.72'});
    }
    path(bust,'M 103 174 C 125 168 144 170 160 177 C 183 166 206 171 225 185',{fill:'none',stroke:ink,'stroke-width':'1.3',opacity:'.53'});
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
