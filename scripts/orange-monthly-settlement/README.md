# 橙子月结脚本工具集

> 把 2026-08-05/06 给「橙子月结」base 做的所有操作打包成可参数化的脚本。
> 任何钉钉 AI 表格场景都能复用，不限于橙子月结。

## 📂 文件清单

| 文件 | 作用 | 何时跑 |
|---|---|---|
| `bulk_rename_fields.py` | 批量给字段名前加前缀（✍️/🔒/🔗） | 新表第一次用、采购/财务/老板角色隔离 |
| `bulk_create_aging_formulas.py` | 给账龄表加 14 个账龄公式字段 | 新建账龄表、或月份切换时重跑 |
| `create_procurement_views.py` | 建「采购录入视图」「采购账龄视图」 | 新表第一次用 |
| `generate_purchase_manual.py` | 生成「采购操作手册」智能文档 | 新场景首次落地、或升级手册版本 |

## 🚀 快速上手

每个脚本都有 `--dry-run` 和 `--confirm` 两个模式：

```bash
# 1. 先预览
python3 bulk_rename_fields.py --base-id <B> --table-id <T> --dry-run

# 2. 再确认
python3 bulk_rename_fields.py --base-id <B> --table-id <T> --confirm
```

## 📍 橙子月结 base 关键 ID（直接复制）

| 名称 | ID |
|---|---|
| Base | `R1zknDm0WRkAqZ67H0qAExeAVBQEx5rG` |
| 橙子月结表 | `TOToCBJ` |
| 2026年账龄分析表 | `fGNFHxA` |
| 供应商货款管理文件夹 | `cEuztXGwpntl` |

## ⚠️ 重要提醒

1. **field_id 是 base 专属**：上面 `create_procurement_views.py` 里硬编码的 field_id 只对「橙子月结 base」有效。其他 base 要重新跑 `dws aitable field list` 拿。
2. **公式不能动态当前月**：账龄公式里的"当前月"是写死的（2026-08）。下个月要重跑 `bulk_create_aging_formulas.py --current-month 2026-09`。
3. **dws CLI 必须已登录**：所有脚本都通过 `dws aitable` 命令调用，需要钉钉 connector 授权。
4. **tencentdocs CLI 必须已登录**：`generate_purchase_manual.py` 通过 tencentdocs.py 调用，需要腾讯文档授权。
5. **每月例行任务**：
   - 月初：重跑 `bulk_create_aging_formulas.py` 加新月份字段
   - 季度：升级 `generate_purchase_manual.py` 模板里"示例"部分

## 📚 前缀规则说明（与钉钉表配合使用）

| 前缀 | 含义 | 谁填 |
|---|---|---|
| ✍️ | 业务人员手填 | 采购/财务 |
| 🔒 | 公式自动算 | 无人（自动） |
| 🔗 | 系统双向链接 | 无人（自动） |

## 🔧 脚本依赖

- Python 3.10+
- `dws` CLI（钉钉 connector）
- `tencentdocs.py`（腾讯文档插件）

## 📜 变更日志

- 2026-08-06：初版打包（4 个脚本 + README）