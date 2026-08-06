#!/usr/bin/env python3
"""
create_procurement_views.py
===========================
给钉钉 AI 表格建"采购专用视图"，控制 visibleFieldIds 让采购只看到该看的字段。

支持两类视图：
  1. 采购录入视图（基于「橙子月结」表）
     - 显式列出手填字段的 fieldId
  2. 采购账龄视图（基于「2026年账龄分析」表）
     - 显式列出供应商简称 + 14 个账龄公式的 fieldId

⚠️ 钉钉 aitable API 的 visibleFieldIds 只控制列顺序，不真"隐藏"列。
   想真隐藏请到钉钉客户端手动操作列设置。
   本脚本的语义是「把采购该看的列排在最前」。

使用：
  python3 create_procurement_views.py --base-id <B> --dry-run
  python3 create_procurement_views.py --base-id <B> --confirm
"""
import argparse
import json
import subprocess
import sys


# 橙子月结 13 个字段 ID（2026-08-06 砍到 13 字段：12 手填 + 1 公式）
ORANGE_MONTHLY_MANUAL = [
    'jvau2tf53bw2ycmiekir7',  # 供应商编码
    '67w2cheqssi95tr83ue4r',  # 简称
    '8cv1d332u6lbkszwp6dto',  # 供应商名称
    'c0dumfgf5eifpa9fz5grv',  # 对账单金额
    'imw7qr8r6yboxlmo0479g',  # 年份
    'otzb1k5amgizlfq9vbmcd',  # 合同及对账单
    '883scyr2f560057dfkwhd',  # 结算方式
    'ep8bil8xe4gh5toxnmdza',  # 开票情况
    'r7i9vytcnyy5n2k7p9tzr',  # 收票日期
    '5bnmjibdevhx54wnc845o',  # 应付款年月日
    'gbapt2go75n9uh81rbnom',  # 已付款金额
    'gn2wxfjwbtx6mngik4y6g',  # 未付金额（公式）
    '4ript77itdqcwyywe2r2b',  # 出账情况备注
]

# 2026年账龄分析 15 个字段（供应商简称 + 14 个账龄公式）
# 【2026-08-06】账龄公式字段 ID 会随月份变化，跑 bulk_create_aging_formulas.py 后更新这里
AGING_VIEW = [
    'qiPjAtc',  # 供应商简称
    'vnBDsqN',  # 本月到期金额
    '4Xb5HPN',  # 逾期1个月金额
    'jhztUjD',  # 逾期2个月金额
    'sa7xrP2',  # 逾期3个月金额
    'eb5ghTB',  # 逾期4个月金额
    'Ji3bTdv',  # 逾期5个月金额
    'A860wgs',  # 逾期6个月金额
    'GKJoPGi',  # 逾期7个月金额
    '2i8OzQK',  # 逾期8个月金额
    'R9kXReh',  # 逾期9个月金额
    '1dyv6J4',  # 逾期10个月金额
    'GcCx5K5',  # 逾期11个月金额
    'fYTrsAE',  # 逾期12个月金额
    'zDFKKmj',  # 逾期13个月及以上
]


def create_view(base_id, table_id, view_name, view_type, field_ids):
    """调 dws aitable view create"""
    config = json.dumps({'visibleFieldIds': field_ids}, ensure_ascii=False)
    cmd = ['dws', 'aitable', 'view', 'create',
           '--base-id', base_id, '--table-id', table_id,
           '--view-type', view_type, '--name', view_name,
           '--config', config, '--format', 'json']
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    return r


def main():
    ap = argparse.ArgumentParser(description='创建采购专用视图')
    ap.add_argument('--base-id', required=True, help='base ID')
    ap.add_argument('--orange-table-id', default='TOToCBJ',
                    help='橙子月结表 ID（默认 TOToCBJ）')
    ap.add_argument('--aging-table-id', default='fGNFHxA',
                    help='2026年账龄分析表 ID（默认 fGNFHxA）')
    ap.add_argument('--skip-orange', action='store_true',
                    help='跳过橙子月结视图')
    ap.add_argument('--skip-aging', action='store_true',
                    help='跳过账龄视图')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--confirm', action='store_true')
    args = ap.parse_args()

    targets = []
    if not args.skip_orange:
        targets.append(('采购录入视图', args.orange_table_id, 'Grid', ORANGE_MONTHLY_MANUAL))
    if not args.skip_aging:
        targets.append(('采购账龄视图', args.aging_table_id, 'Grid', AGING_VIEW))

    for name, table_id, vtype, fids in targets:
        print(f'\n📋 视图「{name}」table={table_id} 列数={len(fids)}')

    if args.dry_run:
        print('\n🚫 --dry-run 模式，未修改')
        return

    if not args.confirm:
        print('\n⚠️  加上 --confirm 才真创建')
        return

    for name, table_id, vtype, fids in targets:
        r = create_view(args.base_id, table_id, name, vtype, fids)
        if r.returncode == 0:
            data = json.loads(r.stdout)
            print(f"✅ {name} | viewId={data.get('data', {}).get('viewId', '?')}")
        else:
            print(f"❌ {name} | {r.stderr.strip()[:200]}")


if __name__ == '__main__':
    main()