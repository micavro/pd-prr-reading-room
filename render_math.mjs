import katex from 'katex';
let input = '';
for await (const chunk of process.stdin) input += chunk;
const expressions = JSON.parse(input);
const rendered = {};
for (const expression of expressions) {
  const block = expression.startsWith('\\[');
  rendered[expression] = katex.renderToString(expression.slice(2, -2), {
    output: 'mathml', displayMode: block, throwOnError: true, strict: 'error'
  });
}
process.stdout.write(JSON.stringify(rendered));
