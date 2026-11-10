// Read-only check against the installed DSH provider; no model/API invocation.
import { resolve, join } from 'node:path';
import { pathToFileURL } from 'node:url';
import { readFile } from 'node:fs/promises';

const packageRoot = process.argv[2];
if (!packageRoot) throw new Error('Usage: node scripts/verify-dsh.mjs <path-to-@deepseek-ai> [workspace]');
const pkg = name => pathToFileURL(join(resolve(packageRoot), name, 'lib/index.js')).href;
const { FileSystemSkillProvider } = await import(pkg('dsh-skill-filesystem'));
const { discoverBaselineInstructionFiles } = await import(pkg('dsh-agent-instructions'));
const warnings = [];
const ctx = { get: () => undefined, logger: { warn: message => warnings.push(message), debug: () => {} } };
const control = { invalidate() {}, signal: new AbortController().signal };
const provider = new FileSystemSkillProvider(ctx, control, { watch: false });
const cwd = resolve(process.argv[3] || process.cwd());
try {
  const result = await provider.list({ cwd });
  const candidates = Array.isArray(result) ? result : result.candidates;
  const found = candidates.filter(skill => skill.name === 'github-first').sort((a, b) => a.rank - b.rank);
  if (!found.length) throw new Error('github-first was not discovered by the installed DSH provider.');
  const skill = await provider.get(found[0], { cwd });
  if (!skill?.content.includes('## 宿主适配') || !skill.invocation.modelInvocable || !skill.invocation.userInvocable) {
    throw new Error('DSH could not load the updated, invocable skill.');
  }
  const files = await discoverBaselineInstructionFiles({ cwd });
  const rules = [];
  for (const file of files) {
    const content = await readFile(file.absolutePath, 'utf8');
    if (content.includes('github-first:begin')) rules.push(file.displayPath);
  }
  if (!rules.length) throw new Error('Managed github-first rules were not discovered. Install with --with-rules.');
  console.log(JSON.stringify({ discovered: true, source: skill.source, invocation: skill.invocation,
    rules, duplicateCandidates: found.length, providerWarnings: warnings.length,
    modelCallMade: false }, null, 2));
} finally {
  await provider.dispose();
}
