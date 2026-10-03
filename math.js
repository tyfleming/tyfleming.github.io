document.addEventListener('DOMContentLoaded', () => {
  const methods = document.getElementById('equations');
  if (!methods || typeof renderMathInElement !== 'function') return;

  renderMathInElement(methods, {
    delimiters: [
      {left: '$$', right: '$$', display: true},
      {left: '\\(', right: '\\)', display: false}
    ],
    output: 'htmlAndMathml',
    throwOnError: true,
    errorCallback: (message, error) => console.error('Sleep equation:', message, error)
  });
});
