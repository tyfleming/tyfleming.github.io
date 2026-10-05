// A deterministic SVG point field, drawn locally without image assets or libraries.
(() => {
  const NS = 'http://www.w3.org/2000/svg';
  const make = (name, attributes = {}) => {
    const element = document.createElementNS(NS, name);
    for (const [key, value] of Object.entries(attributes)) element.setAttribute(key, value);
    return element;
  };

  // The right-facing profile and inner cortical field share the same lattice.
  // They are illustrative geometry; neither encodes subject or model data.
  const profile = 'M 110 17 C 74 17 47 46 46 79 C 45 111 61 140 88 151 L 94 158 L 97 209 L 150 209 L 145 168 C 161 162 174 151 178 142 L 173 135 L 185 132 L 187 126 L 179 121 C 191 119 202 111 205 105 C 205 101 198 99 191 95 L 178 86 C 176 46 150 17 110 17 Z';
  const cortex = 'M 71 77 C 69 55 87 35 109 32 C 135 28 155 45 161 65 C 166 85 150 101 132 106 C 109 113 83 103 74 89 C 72 85 71 81 71 77 Z';

  document.querySelectorAll('[data-point-grid]').forEach((host, index) => {
    const svg = make('svg', { viewBox: '0 0 260 230', focusable: 'false', 'aria-hidden': 'true', preserveAspectRatio: 'xMidYMid meet' });
    const defs = make('defs');
    const profileId = `point-profile-${index}`;
    const cortexId = `point-cortex-${index}`;
    const profileClip = make('clipPath', { id: profileId });
    profileClip.append(make('path', { d: profile }));
    const cortexClip = make('clipPath', { id: cortexId });
    cortexClip.append(make('path', { d: cortex }));
    defs.append(profileClip, cortexClip);
    svg.append(defs);

    const background = make('g', { fill: '#ccd8d2', opacity: '.68' });
    const face = make('g', { fill: '#406a64', 'clip-path': `url(#${profileId})` });
    const brain = make('g', { fill: '#a66c50', 'clip-path': `url(#${cortexId})` });
    for (let row = 0; row < 20; row++) {
      for (let col = 0; col < 22; col++) {
        const x = 16 + col * 10.5;
        const y = 16 + row * 10.5;
        background.append(make('circle', { cx: x, cy: y, r: 1.05 }));
        face.append(make('circle', { cx: x, cy: y, r: 1.85 }));
        brain.append(make('circle', { cx: x, cy: y, r: 2.25 }));
      }
    }
    svg.append(background, face, brain);
    host.replaceChildren(svg);
  });
})();
