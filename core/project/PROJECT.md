# Project: __PROJECT_NAME__

## 目标

_一句话描述这个项目要达成什么。_

## 范围

- 要做：
- 不做（Phase 边界）：

## 约束

- 来自用户/上级的硬约束、安全边界、许可限制：
- Project OS 规范：`.project/` 是唯一长期状态真相源，不制造平行状态文件。

## 架构概览

- 主要模块/目录职责；推荐布局：`docs/`(长期设计) `experiments/`(正式实验) `data/raw/`(只读) `paper/`(论点) `outputs/`(输出) `.scratch/`(草稿)

## 权威位置

- 控制面：`.project/{PROJECT,STATE,PLAN,DECISIONS,HANDOFF}.md`、`EXPERIMENT_GATE.json`、`archive/`
- 阅读顺序：AGENTS.md → PROJECT → STATE → PLAN → HANDOFF → 相关代码/实验