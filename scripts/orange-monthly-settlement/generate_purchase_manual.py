#!/usr/bin/env python3
"""
generate_purchase_manual.py
===========================
生成「橙子月结 采购操作手册」智能文档（v2 模板）。

智能文档内容：
  一、在哪填（base/表/视图切换）
  二、要手填的 15 个字段（含「什么情况下填」列）
  三、不要动的 31 个字段（按 4 类细分）
  四、填写时机（4 个场景 → 对应字段清单）
  五、示例（艾富瑞 2026-08 对账单）
  六、账龄分析怎么看（账龄表 14 列说明）
  七、后续支持

使用：
  python3 generate_purchase_manual.py --title "橙子月结 采购操作手册 v3" \\
      --folder-id cEuztXGwpntl --dry-run

  python3 generate_purchase_manual.py --title "..." --folder-id <F> --confirm

依赖：
  - tencent-docs skill CLI 路径在 ~/.workbuddy/plugins/cache/...
  - 已通过 tencent-docs skill 授权
"""
import argparse
import json
import subprocess
import sys


# 智能文档 MDX 内容（v2 模板）
# 注意：MDX 标签遵循「腾讯文档 smartcanvas 规范」
#   严禁：<Quote> <strong> Markdown **bold
#   规范：<BlockQuote> <Mark bold> <Table> <Todo> <Callout> <ColumnList> <Heading> <BulletedList>
MDX_TEMPLATE = """<Heading>一、在哪填</Heading>

<BlockQuote>📍 <Mark bold>打开路径</Mark>：钉钉 → 「橙子月结」base → 左侧切到 <Mark bold>「采购录入视图」</Mark>（不是默认「表格视图」）
<Mark bold>不要切换</Mark>到「副本供应商付款情况登记表_已更新-艾富瑞」「2026年账龄分析」等其他表</BlockQuote>

<Todo>采购 80% 的时间都只在「采购录入视图」这一个视图里录入对账单</Todo>

<Heading>二、要手填的 15 个字段</Heading>

<BlockQuote>字段名前带 <Mark bold>✍️</Mark> 的是手填字段；带 🔒 的是公式自动算；带 🔗 的是系统链接</BlockQuote>

<Table readonly>
<TableRow>
<TableCell>序号</TableCell>
<TableCell>字段名</TableCell>
<TableCell>类型</TableCell>
<TableCell>什么情况下填</TableCell>
</TableRow>
<TableRow>
<TableCell>1</TableCell>
<TableCell>✍️供应商编码</TableCell>
<TableCell>文本</TableCell>
<TableCell>对照「供应商品牌主数据」填编码</TableCell>
</TableRow>
<TableRow>
<TableCell>2</TableCell>
<TableCell>✍️简称</TableCell>
<TableCell>文本</TableCell>
<TableCell>供应商简写</TableCell>
</TableRow>
<TableRow><TableCell>3</TableCell><TableCell>✍️供应商名称</TableCell><TableCell>文本</TableCell><TableCell>完整公司名</TableCell></TableRow>
<TableRow><TableCell>4</TableCell><TableCell>✍️对账单金额</TableCell><TableCell>数字</TableCell><TableCell>票面金额</TableCell></TableRow>
<TableRow><TableCell>5</TableCell><TableCell>✍️年份</TableCell><TableCell>文本</TableCell><TableCell>4 位年份如 2026</TableCell></TableRow>
<TableRow><TableCell>6</TableCell><TableCell>✍️合同及对账单</TableCell><TableCell>文本</TableCell><TableCell>合同编号或对账单号</TableCell></TableRow>
<TableRow><TableCell>7</TableCell><TableCell>✍️结算方式</TableCell><TableCell>单选(51)</TableCell><TableCell>票到 30/60/90 天、月结…</TableCell></TableRow>
<TableRow><TableCell>8</TableCell><TableCell>✍️开票情况</TableCell><TableCell>多选(7)</TableCell><TableCell>已开票/部分开票/未开票</TableCell></TableRow>
<TableRow><TableCell>9</TableCell><TableCell>✍️收票日期</TableCell><TableCell>文本</TableCell><TableCell>yyyy-mm-dd（注意是文本格式）</TableCell></TableRow>
<TableRow><TableCell>10</TableCell><TableCell>✍️应付款年月日</TableCell><TableCell>日期</TableCell><TableCell>关键：根据结算方式算出到期日</TableCell></TableRow>
<TableRow><TableCell>11</TableCell><TableCell>✍️已付款金额</TableCell><TableCell>数字</TableCell><TableCell>默认 0，财务付款后改</TableCell></TableRow>
<TableRow><TableCell>12</TableCell><TableCell>✍️出账情况备注</TableCell><TableCell>文本</TableCell><TableCell>异常备注</TableCell></TableRow>
<TableRow><TableCell>13</TableCell><TableCell>✍️应付款年月</TableCell><TableCell>文本</TableCell><TableCell>yyyy-mm 形式</TableCell></TableRow>
<TableRow><TableCell>14</TableCell><TableCell>✍️付款申请单提交至财务日期</TableCell><TableCell>日期</TableCell><TableCell>提单那天</TableCell></TableRow>
<TableRow><TableCell>15</TableCell><TableCell>✍️系统发票单号</TableCell><TableCell>文本</TableCell><TableCell>财务那边回填</TableCell></TableRow>
</Table>

<Heading>三、不要动的 31 个字段</Heading>

<Callout>⚠️ 采购不要触碰任何 🔒 或 🔗 前缀的字段，动了会断公式或关联</Callout>

<BulletedList>
<BulletedListItem>🔒<Mark bold>未付金额</Mark>（公式自动算 = 对账单金额 − 已付款金额）</BulletedListItem>
<BulletedListItem>🔒 27 个月份字段（_sys_月份未付/已付 2025-06 ~ 2026-10，给账龄表做透视）</BulletedListItem>
<BulletedListItem>🔗 4 个双向链接（🔗_镜像/关键，动了会断关联）</BulletedListItem>
</BulletedList>

<Heading>四、填写时机</Heading>

<ColumnList>
<Column>
<Callout>📅 收到供应商对账单</Callout>
<BulletedList>
<BulletedListItem>填 ✍️1-10 字段（供应商信息 + 金额 + 收票日 + 应付款年月日）</BulletedListItem>
</BulletedList>
</Column>
<Column>
<Callout>💰 提交付款申请</Callout>
<BulletedList>
<BulletedListItem>填 ✍️14（付款申请单提交至财务日期）</BulletedListItem>
</BulletedList>
</Column>
<Column>
<Callout>✅ 财务付款后</Callout>
<BulletedList>
<BulletedListItem>财务填 ✍️11（已付款金额）和 ✍️15（系统发票单号）</BulletedListItem>
</BulletedList>
</Column>
<Column>
<Callout>⚠️ 有异常</Callout>
<BulletedList>
<BulletedListItem>填 ✍️12（出账情况备注）</BulletedListItem>
</BulletedList>
</Column>
</ColumnList>

<Heading>五、示例</Heading>

<Callout>📝 艾富瑞 2026-08 对账单录入示例</Callout>

<Table readonly>
<TableRow>
<TableCell>字段</TableCell>
<TableCell>示例值</TableCell>
</TableRow>
<TableRow><TableCell>供应商编码</TableCell><TableCell>AIF-2024-001</TableCell></TableRow>
<TableRow><TableCell>简称</TableCell><TableCell>艾富瑞</TableCell></TableRow>
<TableRow><TableCell>对账单金额</TableCell><TableCell>50000</TableCell></TableRow>
<TableRow><TableCell>收票日期</TableCell><TableCell>2026-08-15</TableCell></TableRow>
<TableRow><TableCell>结算方式</TableCell><TableCell>月结 60 天</TableCell></TableRow>
<TableRow><TableCell>应付款年月日</TableCell><TableCell>2026-10-14</TableCell></TableRow>
<TableRow><TableCell>应付款年月</TableCell><TableCell>2026-10</TableCell></TableRow>
</Table>

<Heading>六、账龄分析怎么看</Heading>

<BlockQuote>📍 <Mark bold>打开路径</Mark>：钉钉 → 「2026年账龄分析」表 → 左侧切到 <Mark bold>「采购账龄视图」</Mark></BlockQuote>

<Table readonly>
<TableRow>
<TableCell>字段</TableCell>
<TableCell>含义</TableCell>
<TableCell>采购怎么用</TableCell>
</TableRow>
<TableRow><TableCell>🔒本月到期金额</TableCell><TableCell>本月应付未付</TableCell><TableCell>准备付款</TableCell></TableRow>
<TableRow><TableCell>🔒逾期 1-3 个月</TableCell><TableCell>刚刚逾期</TableCell><TableCell>催款第一波</TableCell></TableRow>
<TableRow><TableCell>🔒逾期 4-6 个月</TableCell><TableCell>中期逾期</TableCell><TableCell>催款第二波</TableCell></TableRow>
<TableRow><TableCell>🔒逾期 7-12 个月</TableCell><TableCell>长期逾期</TableCell><TableCell>升级到老板</TableCell></TableRow>
<TableRow><TableCell>🔒逾期 13 个月及以上</TableCell><TableCell>历史遗留</TableCell><TableCell>走法务流程</TableCell></TableRow>
</Table>

<Heading>七、后续支持</Heading>

<Todo>遇到不会填的字段，先看手册</Todo>
<Todo>操作异常找财务协调</Todo>
<Todo>方案升级找 IT</Todo>
"""


def create_doc(title, mdx_content):
    """调 tencentdocs CLI 创建智能文档"""
    payload = json.dumps({'title': title, 'mdx': mdx_content},
                         ensure_ascii=False)
    cmd = ['python3', 'tencentdocs.py', 'tdoc_call',
           'tencent-docs', 'create_smartcanvas_by_mdx', payload]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    return r


def move_to_folder(file_id, folder_id):
    cmd = ['python3', 'tencentdocs.py', 'tdoc_call',
           'tencent-docs', 'manage.move_file',
           json.dumps({'file_id': file_id, 'target_folder_id': folder_id},
                       ensure_ascii=False)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    return r


def main():
    ap = argparse.ArgumentParser(description='生成采购操作手册智能文档')
    ap.add_argument('--title', required=True, help='文档标题')
    ap.add_argument('--folder-id', required=True, help='目标文件夹 ID')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--confirm', action='store_true')
    args = ap.parse_args()

    print(f'📄 文档标题: {args.title}')
    print(f'📁 目标文件夹: {args.folder_id}')
    print(f'📏 MDX 长度: {len(MDX_TEMPLATE)} 字符')

    if args.dry_run:
        print('\n🚫 --dry-run 模式，未生成')
        return

    if not args.confirm:
        print('\n⚠️  加上 --confirm 才真生成')
        return

    print('\n🚀 生成智能文档...')
    r = create_doc(args.title, MDX_TEMPLATE)
    if r.returncode != 0:
        print(f'❌ 创建失败: {r.stderr.strip()[:300]}')
        sys.exit(1)
    data = json.loads(r.stdout)
    result = json.loads(data['result']['content'][0]['text'])
    file_id = result.get('file_id')
    url = result.get('url')
    print(f'✅ 文档创建成功')
    print(f'   file_id: {file_id}')
    print(f'   url: {url}?_fid={file_id}')

    print(f'\n📁 移动到文件夹 {args.folder_id}...')
    r2 = move_to_folder(file_id, args.folder_id)
    if r2.returncode == 0:
        print('✅ 已移动到目标文件夹')
    else:
        print(f'⚠️  移动失败: {r2.stderr.strip()[:200]}（可手动移）')


if __name__ == '__main__':
    main()