#!/usr/bin/env python3
"""
bulk_create_aging_formulas.py
=============================
给「2026年账龄分析」表加 14 个新公式字段，按账龄月数展示未付金额。

核心公式：
  本月到期金额       = [自动汇总 月份未付 YYYY-MM]         (当前月)
  逾期 1 个月金额   = [自动汇总 月份未付 YYYY-MM]         (上 1 个月)
  ...
  逾期 12 个月金额  = [自动汇总 月份未付 YYYY-MM]         (上 12 个月)
  逾期 13 个月及以上 = SUM([2025-07],[2025-06],[2025-06及以前])

⚠️ 当前月是写死的（2026-08），下个月需要手动改 --current-month。

使用：
  python3 bulk_create_aging_formulas.py --base-id <B> --table-id <T> \\
      --current-month 2026-08 --dry-run

  python3 bulk_create_aging_formulas.py --base-id <B> --table-id <T> \\
      --current-month 2026-08 --confirm

依赖：
  - 「自动汇总 月份未付 YYYY-MM」字段必须已存在（橙子月结方案里 ✅ 已建）
"""
import argparse
import json
import subprocess
import concurrent.futures
import sys
from datetime import datetime


def offset_month(yyyymm: str, delta: int) -> str:
    """yyyy-mm 字符串加减月份"""
    y, m = map(int, yyyymm.split('-'))
    dt = datetime(y, m, 1)
    if delta >= 0:
        for _ in range(delta):
            if m == 12:
                y, m = y + 1, 1
            else:
                m += 1
    else:
        for _ in range(-delta):
            if m == 1:
                y, m = y - 1, 12
            else:
                m -= 1
    return f'{y:04d}-{m:02d}'


def build_fields(current_month: str):
    """生成 14 个公式字段定义"""
    fields = []
    # 本月到期
    fields.append({
        'fieldName': f'本月到期金额',
        'type': 'formula',
        'config': {'formatter': 'FLOAT_2',
                   'formula': f'[自动汇总 月份未付 {current_month}]'}
    })
    # 逾期 1-12 月
    for i in range(1, 13):
        target = offset_month(current_month, -i)
        fields.append({
            'fieldName': f'逾期{i}个月金额',
            'type': 'formula',
            'config': {'formatter': 'FLOAT_2',
                       'formula': f'[自动汇总 月份未付 {target}]'}
        })
    # 逾期 13 月及以上（剩余全部历史月份求和）
    m13 = offset_month(current_month, -13)
    m14 = offset_month(current_month, -14)
    fields.append({
        'fieldName': '逾期13个月及以上',
        'type': 'formula',
        'config': {
            'formatter': 'FLOAT_2',
            'formula': f'SUM([自动汇总 月份未付 {m13}],[自动汇总 月份未付 {m14}],[自动汇总 月份未付 {m14}及以前])'
        }
    })
    return fields


def create_fields(base_id, table_id, fields):
    """调 dws aitable field create"""
    payload = json.dumps(fields, ensure_ascii=False)
    cmd = ['dws', 'aitable', 'field', 'create',
           '--base-id', base_id, '--table-id', table_id,
           '--fields', payload, '--format', 'json']
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    return r


def main():
    ap = argparse.ArgumentParser(description='批量给账龄表加 14 个新公式字段')
    ap.add_argument('--base-id', required=True)
    ap.add_argument('--table-id', required=True)
    ap.add_argument('--current-month', default='2026-08',
                    help='当前月 yyyy-mm，下个月改这个参数重跑')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--confirm', action='store_true')
    args = ap.parse_args()

    fields = build_fields(args.current_month)
    print(f'📋 准备创建 {len(fields)} 个公式字段（当前月 {args.current_month}）')
    for f in fields:
        print(f"  🔒{f['fieldName']:18s} | {f['config']['formula']}")

    if args.dry_run:
        print('\n🚫 --dry-run 模式，未修改')
        return

    if not args.confirm:
        print('\n⚠️  加上 --confirm 才真创建（建议先 --dry-run）')
        return

    r = create_fields(args.base_id, args.table_id, fields)
    if r.returncode != 0:
        print(f'❌ 创建失败: {r.stderr.strip()[:300]}')
        sys.exit(1)

    data = json.loads(r.stdout)
    created = data.get('data', {}).get('fields', [])
    ok = sum(1 for f in created if f.get('status') == 'success')
    print(f'\n✅ 成功: {ok}/{len(created)}')
    for f in created:
        status = '✅' if f.get('status') == 'success' else '❌'
        print(f'  {status} {f.get("fieldName")} | {f.get("fieldId")} | {f.get("reason", "-")}')


if __name__ == '__main__':
    main()