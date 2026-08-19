# examples/

本目录留给使用示例。首版最小化：用以下命令即可在任意目录生成一个标准的
Project OS 控制面示例（.project/ + docs/ + experiments/ + outputs/ + .scratch/）：

```bash
python3 ../scripts/init-project.py --dir ./my-example-project --name "Demo"
```

在 OpenCode 中运行该目录后，`research-lead` 会按 `core/policies/CORE.md` 的规则驱动流程。