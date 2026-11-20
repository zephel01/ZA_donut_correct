#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZA ドーナツ厳選マクロのバージョンを、まとめて更新・確認するスクリプト（開発用）。

バージョンが書かれている場所:
  - ZA_donut_correct.py の VERSION = '...'
  - ZA_donut_correct.py の NAME = "ZA ドーナツ厳選 v..."（PCME 0.2.0 は構文解析だけで読むため、文字列リテラル）
  - README.md・docs/*.md の <!-- version -->...<!-- /version --> で囲んだ部分
  - README.md のバッジ（img.shields.io/badge/version-...）
  - docs/*.md に書いたコマンド名 "ZA ドーナツ厳選 v..."
  - CHANGELOG.md の見出し ## [...] とリンク

使い方:
  python tools/bump_version.py 2.2.0        バージョンを 2.2.0 に上げる（CHANGELOG の Unreleased を 2.2.0 に移す）
  python tools/bump_version.py 2.2.0 --dry-run   書き換える内容だけ表示する
  python tools/bump_version.py --check      すべての場所がそろっているか確認する（ずれていれば終了コード 1）
  python tools/bump_version.py --print      今のバージョンを表示する
  python tools/bump_version.py --notes      CHANGELOG の今のバージョンの部分を表示する（Release の本文用）
"""

import argparse
import ast
import datetime
import glob
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
MAIN = os.path.join(ROOT, 'ZA_donut_correct.py')
README = os.path.join(ROOT, 'README.md')
CHANGELOG = os.path.join(ROOT, 'CHANGELOG.md')
COMMAND_CLASS = 'ZA_DonutV188'
NAME_PREFIX = 'ZA ドーナツ厳選 v'
REPO_URL = 'https://github.com/zephel01/ZA_donut_correct'

SEMVER = r'\d+\.\d+\.\d+'
RE_VERSION_LINE = re.compile(r"^(VERSION\s*=\s*)(['\"])(" + SEMVER + r")\2", re.M)
RE_NAME_LINE = re.compile(r'^(\s*NAME\s*=\s*)(["\'])' + re.escape(NAME_PREFIX) + r'(' + SEMVER + r')\2', re.M)
RE_MARKER = re.compile(r'(<!-- version -->)(.*?)(<!-- /version -->)')
RE_BADGE = re.compile(r'(img\.shields\.io/badge/version-)(' + SEMVER + r')(-)')
RE_NAME_REF = re.compile(r'(")' + re.escape(NAME_PREFIX) + r'(' + SEMVER + r')(")')


def _read(path):
    # 改行コード（CRLF / LF）はそのまま残す
    with open(path, 'r', encoding='utf-8', newline='') as f:
        return f.read()


def _write(path, text):
    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(text)


def _rel(path):
    return os.path.relpath(path, ROOT)


def markdown_files():
    files = [README] + sorted(glob.glob(os.path.join(ROOT, 'docs', '*.md')))
    return [f for f in files if os.path.exists(f)]


def read_main():
    """ZA_donut_correct.py から (VERSION, NAME, NAME が文字列リテラルか) を、実行せずに読む"""
    tree = ast.parse(_read(MAIN), filename=MAIN)
    version = None
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'VERSION' for t in node.targets):
            try:
                version = ast.literal_eval(node.value)
            except Exception:
                version = None
    name, literal = None, False
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == COMMAND_CLASS:
            for stmt in node.body:
                if isinstance(stmt, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'NAME' for t in stmt.targets):
                    # PCME 0.2.0 の CommandLoader と同じ読み方（ast.literal_eval）
                    try:
                        name = ast.literal_eval(stmt.value)
                        literal = isinstance(name, str)
                    except Exception:
                        name, literal = ast.unparse(stmt.value), False
    return version, name, literal


def changelog_sections(text):
    """[(見出しのバージョン or 'Unreleased', 見出しの行の位置, 本文の終わりの位置)]"""
    heads = [(m.group(1), m.start(), m.end()) for m in re.finditer(r'^## \[([^\]]+)\][^\n]*\n', text, re.M)]
    result = []
    for i, (ver, start, body_start) in enumerate(heads):
        end = heads[i + 1][1] if i + 1 < len(heads) else len(text)
        m = re.search(r'^\[[^\]]+\]: ', text[body_start:end], re.M)       # 末尾のリンク定義の前まで
        if m:
            end = body_start + m.start()
        result.append((ver, start, body_start, end))
    return result


# --------------------------------------------------------------------------- 確認
def check():
    problems = []
    version, name, literal = read_main()
    if not version or not re.fullmatch(SEMVER, str(version)):
        problems.append(f"{_rel(MAIN)}: VERSION が読めません（VERSION = 'X.Y.Z' の形にしてください）")
        return problems, version
    if not literal:
        problems.append(f"{_rel(MAIN)}: {COMMAND_CLASS}.NAME が文字列リテラルではありません（{name}）。"
                        f"PCME 0.2.0 ではコマンド一覧に出ません")
    elif name != NAME_PREFIX + version:
        problems.append(f"{_rel(MAIN)}: NAME \"{name}\" が VERSION {version} と合っていません")

    for path in markdown_files():
        text = _read(path)
        for m in RE_MARKER.finditer(text):
            if m.group(2) != version:
                line = text.count('\n', 0, m.start()) + 1
                problems.append(f"{_rel(path)}:{line}: 版表示が {m.group(2)}（{version} にしてください）")
        for m in RE_BADGE.finditer(text):
            if m.group(2) != version:
                line = text.count('\n', 0, m.start()) + 1
                problems.append(f"{_rel(path)}:{line}: version バッジが {m.group(2)}")
        for m in RE_NAME_REF.finditer(text):
            if m.group(2) != version:
                line = text.count('\n', 0, m.start()) + 1
                problems.append(f"{_rel(path)}:{line}: コマンド名 \"{NAME_PREFIX}{m.group(2)}\" が古いです")
        # 「ZA ドーナツ厳選 v2.1.0」のように直書きした版は、更新で直らないので知らせる
        for m in re.finditer(re.escape(NAME_PREFIX) + r'(' + SEMVER + r')', text):
            if m.start() > 0 and text[m.start() - 1] == '"':
                continue                                   # "ZA ドーナツ厳選 vX.Y.Z"（コマンド名の例）は上で確認
            line = text.count('\n', 0, m.start()) + 1
            problems.append(f"{_rel(path)}:{line}: コマンド名の版が直書きです。"
                            f"ZA ドーナツ厳選 v<!-- version -->{version}<!-- /version --> にしてください")
    if not RE_MARKER.search(_read(README)):
        problems.append(f"{_rel(README)}: <!-- version -->...<!-- /version --> が見つかりません")

    if not os.path.exists(CHANGELOG):
        problems.append(f"{_rel(CHANGELOG)} がありません")
    else:
        text = _read(CHANGELOG)
        versions = [v for v, *_ in changelog_sections(text)]
        if 'Unreleased' not in versions:
            problems.append(f"{_rel(CHANGELOG)}: ## [Unreleased] がありません")
        if version not in versions:
            problems.append(f"{_rel(CHANGELOG)}: ## [{version}] の見出しがありません")
        if f'[{version}]: ' not in text:
            problems.append(f"{_rel(CHANGELOG)}: [{version}] のリンクがありません")
    return problems, version


# --------------------------------------------------------------------------- 更新
def bump(new, dry_run=False, allow_empty=False, today=None):
    if not re.fullmatch(SEMVER, new):
        sys.exit(f"バージョンは X.Y.Z の形で指定してください: {new}")
    old, _, literal = read_main()
    if not old:
        sys.exit("ZA_donut_correct.py の VERSION が読めません")
    if tuple(map(int, new.split('.'))) <= tuple(map(int, old.split('.'))):
        sys.exit(f"新しいバージョン {new} は、今の {old} より大きくしてください")
    if not literal:
        sys.exit("NAME が文字列リテラルではありません。先に NAME = \"ZA ドーナツ厳選 vX.Y.Z\" の形に直してください")

    changes = {}

    # ZA_donut_correct.py
    text = _read(MAIN)
    text, n1 = RE_VERSION_LINE.subn(lambda m: f"{m.group(1)}{m.group(2)}{new}{m.group(2)}", text, count=1)
    text, n2 = RE_NAME_LINE.subn(lambda m: f"{m.group(1)}{m.group(2)}{NAME_PREFIX}{new}{m.group(2)}", text, count=1)
    if n1 != 1 or n2 != 1:
        sys.exit("ZA_donut_correct.py の VERSION / NAME の行が見つかりません")
    changes[MAIN] = text

    # README.md・docs/*.md
    for path in markdown_files():
        text = _read(path)
        new_text = RE_MARKER.sub(lambda m: m.group(1) + new + m.group(3), text)
        new_text = RE_BADGE.sub(lambda m: m.group(1) + new + m.group(3), new_text)
        new_text = RE_NAME_REF.sub(lambda m: m.group(1) + NAME_PREFIX + new + m.group(3), new_text)
        if new_text != text:
            changes[path] = new_text

    # CHANGELOG.md: Unreleased の内容を新しい版の見出しの下に移す
    text = _read(CHANGELOG)
    sections = changelog_sections(text)
    unreleased = [s for s in sections if s[0] == 'Unreleased']
    if not unreleased:
        sys.exit("CHANGELOG.md に ## [Unreleased] がありません")
    _, start, body_start, end = unreleased[0]
    body = text[body_start:end].strip('\n')
    if not body.strip() and not allow_empty:
        sys.exit("CHANGELOG.md の ## [Unreleased] が空です。変更点を書いてから実行してください（空のままでよければ --allow-empty）")
    date = (today or datetime.date.today()).isoformat()
    nl = '\r\n' if '\r\n' in text else '\n'
    block = f"## [Unreleased]{nl}{nl}## [{new}] - {date}{nl}{nl}" + (body + nl + nl if body.strip() else '')
    text = text[:start] + block + text[end:].lstrip('\r\n')
    # リンク: Unreleased は vNEW...HEAD、新しい版は tag へ
    text = re.sub(r'^\[Unreleased\]: .*$', f'[Unreleased]: {REPO_URL}/compare/v{new}...HEAD', text, flags=re.M)
    link = f'[{new}]: {REPO_URL}/releases/tag/v{new}'
    if f'[{new}]: ' not in text:
        m = re.search(r'^\[Unreleased\]: .*$', text, flags=re.M)
        if m:
            text = text[:m.end()] + nl + link + text[m.end():]
        else:
            text = text.rstrip('\r\n') + nl + nl + f'[Unreleased]: {REPO_URL}/compare/v{new}...HEAD' + nl + link + nl
    changes[CHANGELOG] = text

    for path, content in changes.items():
        print(("（書き換え予定）" if dry_run else "更新: ") + _rel(path))
        if not dry_run:
            _write(path, content)
    if dry_run:
        return 0
    problems, _ = check()
    if problems:
        print("\n[!] 更新後もずれが残っています:")
        for p in problems:
            print("  - " + p)
        return 1
    print(f"\nv{old} → v{new} に更新しました。git diff で確認してからコミットしてください。")
    return 0


def notes(version=None):
    version = version or read_main()[0]
    text = _read(CHANGELOG)
    for ver, _, body_start, end in changelog_sections(text):
        if ver == version:
            return text[body_start:end].strip()
    sys.exit(f"CHANGELOG.md に ## [{version}] がありません")


def main(argv=None):
    ap = argparse.ArgumentParser(description='ZA ドーナツ厳選マクロのバージョンを更新・確認する')
    ap.add_argument('version', nargs='?', help='新しいバージョン（例: 2.2.0）')
    ap.add_argument('--check', action='store_true', help='すべての場所のバージョンがそろっているか確認する')
    ap.add_argument('--print', dest='print_version', action='store_true', help='今のバージョンを表示する')
    ap.add_argument('--notes', nargs='?', const='', metavar='VERSION', help='CHANGELOG のその版の部分を表示する')
    ap.add_argument('--dry-run', action='store_true', help='書き換えずに、書き換えるファイルだけ表示する')
    ap.add_argument('--allow-empty', action='store_true', help='CHANGELOG の Unreleased が空でも上げる')
    args = ap.parse_args(argv)

    if args.print_version:
        print(read_main()[0])
        return 0
    if args.notes is not None:
        print(notes(args.notes or None))
        return 0
    if args.check:
        problems, version = check()
        if problems:
            print(f"バージョンのずれがあります（ZA_donut_correct.py の VERSION: {version}）:")
            for p in problems:
                print("  - " + p)
            print("\n直し方: python tools/bump_version.py <バージョン> で更新するか、上の場所を合わせてください。")
            return 1
        print(f"OK: すべての場所が v{version} でそろっています。")
        return 0
    if args.version:
        return bump(args.version, dry_run=args.dry_run, allow_empty=args.allow_empty)
    ap.print_help()
    return 2


if __name__ == '__main__':
    sys.exit(main())
