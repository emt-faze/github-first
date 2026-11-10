#!/usr/bin/env python3
"""Install the shared skill locally; standard library only, no network calls."""
import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BEGIN = '<!-- github-first:begin -->'
END = '<!-- github-first:end -->'


def home_path(value, variable, fallback):
    return Path(value or os.environ.get(variable) or fallback).expanduser().resolve()


def tree_bytes(directory):
    return {p.relative_to(directory).as_posix(): p.read_bytes()
            for p in directory.rglob('*') if p.is_file()}


def merge_rules(original, block):
    if BEGIN not in original and END not in original:
        return original + ('\n\n' if original else '') + block + '\n'
    if original.count(BEGIN) != 1 or original.count(END) != 1:
        raise ValueError('Ambiguous github-first markers; merge AGENTS.md manually.')
    start, end = original.index(BEGIN), original.index(END)
    if end < start:
        raise ValueError('Invalid github-first marker order.')
    return original[:start] + block + original[end + len(END):]


def install(args):
    dsh_home = home_path(args.dsh_home, 'DSH_HOME', Path.home() / '.dsh')
    codex_home = home_path(args.codex_home, 'CODEX_HOME', Path.home() / '.codex')
    agents_home = Path(args.agents_home or Path.home() / '.agents').expanduser().resolve()
    if args.target == 'shared':
        dsh_agents = home_path(None, 'DSH_AGENTS_HOME', Path.home() / '.agents')
        if not args.agents_home and dsh_agents != agents_home:
            raise ValueError('DSH_AGENTS_HOME differs from the Codex shared root. Use --target dsh or configure both hosts consistently.')
    base = dsh_home if args.target == 'dsh' else agents_home
    target = base / 'skills' / 'github-first'
    source = ROOT / 'skills' / 'github-first'
    if not (source / 'SKILL.md').is_file():
        raise ValueError('Run this script from a complete repository checkout.')
    # Refuse redirection before any replace/move. Do not follow a skill symlink.
    if target.is_symlink() or (hasattr(os.path, 'isjunction') and os.path.isjunction(target)):
        raise ValueError('Skill destination is a link; manage it manually.')
    if target.resolve().parent != (base / 'skills').resolve():
        raise ValueError('Skill destination escapes the expected skills directory.')
    if target.exists() and not target.is_dir():
        raise ValueError('Skill destination is not a directory.')
    same = target.exists() and tree_bytes(target) == tree_bytes(source)
    if target.exists() and not same and not args.update:
        raise ValueError('Skill already exists and differs. Review it, then use --update to back it up and replace it.')

    template = (ROOT / 'examples' / 'AGENTS.md').read_text(encoding='utf-8')
    block = BEGIN + '\n' + template.rstrip() + '\n\n完整流程文件：`' + (target / 'SKILL.md').as_posix() + '`\n' + END
    rules = [dsh_home / 'AGENTS.md']
    if args.target == 'shared':
        rules.append(codex_home / 'AGENTS.md')
    changes = []
    if args.with_rules:
        for path in dict.fromkeys(rules):
            if path.is_symlink():
                raise ValueError('AGENTS.md is a link; merge rules manually.')
            before = path.read_bytes() if path.exists() else b''
            text = before.decode('utf-8-sig')
            after = merge_rules(text, block)
            bom = b'\xef\xbb\xbf' if before.startswith(b'\xef\xbb\xbf') else b''
            encoded = bom + after.encode('utf-8')
            if encoded != before:
                changes.append((path, before, encoded))

    backup_root = base / 'github-first-backups'
    backup = None
    if (target.exists() and not same) or changes:
        backup_root.mkdir(parents=True, exist_ok=True)
        backup = Path(tempfile.mkdtemp(prefix=datetime.now().strftime('%Y%m%d-%H%M%S-'), dir=backup_root))
    if not same:
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            target.rename(backup / 'skill')
        try:
            shutil.copytree(source, target)
        except Exception:
            # Preserve a partial copy for diagnosis; restore the previous skill.
            if backup is not None and (backup / 'skill').exists():
                if target.exists():
                    target.rename(backup / 'partial-install')
                (backup / 'skill').rename(target)
            raise
    for index, (path, before, after) in enumerate(changes):
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            (backup / f'AGENTS-{index}.md').write_bytes(before)
        temp = path.with_name('AGENTS.github-first.tmp')
        with temp.open('xb') as stream:
            stream.write(after)
        os.replace(temp, path)
    return {'version': json.loads((ROOT / 'plugin.json').read_text(encoding='utf-8'))['version'],
            'skill': str(target), 'rules_updated': [str(p) for p, _, _ in changes],
            'backup': str(backup) if backup else None,
            'note': 'Open a new host session and verify skill discovery. No model request was made.'}


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--target', choices=['dsh', 'shared'], default='dsh')
    p.add_argument('--with-rules', action='store_true', help='Append managed rules while preserving existing instructions.')
    p.add_argument('--update', action='store_true', help='Back up and replace a differing installed skill.')
    p.add_argument('--dsh-home')
    p.add_argument('--codex-home')
    p.add_argument('--agents-home', help='Shared skill root; configure both hosts to scan it when customized.')
    return p


if __name__ == '__main__':
    try:
        print(json.dumps(install(parser().parse_args()), ensure_ascii=False, indent=2))
    except (OSError, ValueError) as error:
        raise SystemExit(str(error))
