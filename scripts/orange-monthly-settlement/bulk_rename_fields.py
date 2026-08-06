#!/usr/bin/env python3
"""
bulk_rename_fields.py
=====================
批量给钉钉 AI 表格字段名前加视觉标记前缀，让采购一眼分清字段类型。

前缀规则（与 2026-08-05 橙子月结方案保持一致）：
  ✍️  - 采购需要手填的字段（text / number / date / singleSelect / multipleSelect 等）
  🔒  - 公式自动算（formula），采购不要动
  🔗  - 系统双向链接（bidirectionalLink），采购不要动

使用：
  python3 bulk_rename_fields.py --base-id R1zknDm0WRkAqZ67H0qAExeAVBQEx5rG \\
      --table-id TOToCBJ --dry-run

  python3 bulk_rename_fields.py --base-id <BASE_ID> --table-id <TABLE_ID> \\
      --confirm

依赖：
  - dws CLI 已登录（钉钉 connector）
"""
import argparse
import json
import subprocess
import concurrent.futures
import sys


def fetch_fields(base_id: str, table_id: str):
    """读取表里所有字段"""
    cmd = ['dws', 'aitable', 'field', 'list',
           '--base-id', base_id, '--table-id', table_id, '--format', 'json']
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    if r.returncode != 0:
        print(f'❌ 读字段失败: {r.stderr.strip()[:200]}')
        sys.exit(1)
    data = json.loads(r.stdout)
    return data['data']['fields']


def classify(fields):
    """字段分类"""
    manual, auto, link = [], [], []
    for f in fields:
        name = f.get('fieldName', '')
        ftype = f.get('type', '')
        fid = f.get('fieldId', '')
        if ftype == 'formula':
            auto.append((fid, name, ftype))
        elif ftype == 'bidirectionalLink':
            link.append((fid, name, ftype))
        else:
            manual.append((fid, name, ftype))
    return manual, auto, link


def plan_renames(manual, auto, link):
    """生成改名计划（跳过已有前缀的字段）"""
    plan = []
    for fid, name, ftype in manual:
        if name.startswith('✍️'):
            continue
        plan.append((fid, name, f'✍️{name}', ftype))
    for fid, name, ftype in auto:
        if name.startswith('🔒') or name.startswith('['):
            continue
        plan.append((fid, name, f'🔒{name}', ftype))
    for fid, name, ftype in link:
        if name.startswith('🔗'):
            continue
        plan.append((fid, name, f'🔗{name}', ftype))
    return plan


def do_rename(base_id, table_id, fid, new_name):
    """单字段改名"""
    cmd = ['dws', 'aitable', 'field', 'update',
           '--base-id', base_id, '--table-id', table_id,
           '--field-id', fid, '--name', new_name, '--format', 'json']
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    if r.returncode == 0:
        return f'✅ {new_name}'
    return f'❌ {new_name} | err: {r.stderr.strip()[:120]}'


def main():
    ap = argparse.ArgumentParser(description='批量给钉钉 AI 表格字段名前加前缀')
    ap.add_argument('--base-id', required=True, help='base ID')
    ap.add_argument('--table-id', required=True, help='table ID')
    ap.add_argument('--dry-run', action='store_true', help='只看不改')
    ap.add_argument('--confirm', action='store_true', help='确认改名')
    args = ap.parse_args()

    print(f'📥 读取字段: base={args.base_id} table={args.table_id}')
    fields = fetch_fields(args.base_id, args.table_id)
    manual, auto, link = classify(fields)

    print(f'   手填 {len(manual)} 个 / 公式 {len(auto)} 个 / 链接 {len(link)} 个')

    plan = plan_renames(manual, auto, link)
    print(f'   待改名 {len(plan)} 个（已带前缀的会跳过）')

    if not plan:
        print('✅ 无需改名')
        return

    print('\n预览前 10 条:')
    for fid, old, new, ftype in plan[:10]:
        print(f'  [{ftype:18s}] {old} → {new}')

    if args.dry_run:
        print('\n🚫 --dry-run 模式，未修改')
        return

    if not args.confirm:
        print('\n⚠️  加上 --confirm 才真改名（建议先 --dry-run）')
        return

    print(f'\n🚀 开始改名 {len(plan)} 个字段...')
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        results = list(ex.map(
            lambda p: do_rename(args.base_id, args.table_id, p[0], p[2]),
            plan))
    for r in results:
        print(r)
    ok = sum(1 for r in results if r.startswith('✅'))
    print(f'\n完成: {ok}/{len(results)}')


if __name__ == '__main__':
    main()