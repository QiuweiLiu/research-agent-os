---
description: Project OS audit — layout, budgets, duplicate control planes, redundancy (read-only)
---
对指定项目跑只读审计并如实汇报 FAIL/WARN，不要修改任何文件。

```sh
python3 ~/.config/opencode/scripts/project_audit.py $ARGUMENTS
```

参数：项目根目录或 `.project/` 路径；也可用 `--discover <dir>` 扫描目录下所有项目。输出后给出最小修复建议（只建议，不改动）。
