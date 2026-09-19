# Jev Frontier 100：Jev 与小模型的九种设置对比

**Jev 得分 77.0%；Qwen3.5 2B／2,048-token 思考得分 82.0%；4B／同档思考得分 96.7%。**
用 100 道原创题，让 Jev 的实际能力边界有一个直观参照。

[English](README.md) · [全部题目](docs/QUESTIONS.md) · [答案与依据](docs/ANSWERS.md) · [完整协议](docs/PROTOCOL.md)

![Jev 与九个 Qwen 设置](results/v0.2-budget/comparison.png)

## 结果与结论

| 思考预算 | Qwen3.5 0.8B | Qwen3.5 2B | Qwen3.5 4B |
|---|---:|---:|---:|
| 关闭 thinking | 38.0% | 48.0% | 56.0% |
| 512 tokens | 39.0% | 59.7% | 78.3% |
| 2,048 tokens | 54.0% | 82.0% | **96.7%** |

**Jev 1.13.0：77.0%。** 每个条件为 100 道题 × 3 轮；共保留 3,000 次有效回答。
不取最好的一轮，也不做多数投票。

- **Jev 明显落后于充分思考的 4B。** 4B／2,048 高出 19.7 个百分点，配对题
  bootstrap 的 95% 差值区间为 **+12.7～+26.7**。
- **Jev 与充分思考的 2B 总体成绩接近。** 2B／2,048 高出 5.0 个百分点，
  差值区间为 **−2.3～+12.3**；不能据此证明两者等价。
- **思考预算不能省略。** 4B 关闭 thinking 只有 56.0%，512 档为 78.3%。
  “不如 4B”的判断必须带上所测思考条件。
- **总分接近不等于能力分布相同。** 本题集上，Jev 在短代码语义和形式逻辑
  上较强，2B／2,048 在关系追踪和算法上更强。见[分领域结果](results/v0.2-budget/RESULTS.md)。

这支持“在当前题集和预算下，Jev 的表现接近充分思考的 2B，明显低于充分
思考的 4B”。100 道题不能证明绝对智力上限，也不能反推 Jev 的参数量。
4B 已接近满分，说明本题集对更强系统的区分能力有限。

## 测了什么

客服、规则应用、语篇理解、形式逻辑、关系推理、数学、时间、代码语义、算法、
证据整合，共十个领域，各十题。50 组反事实配对，60 题有可执行答案来源；
设计难度为简单 30／中等 40／困难 30，尚未独立校准。
题目为 AI 辅助原创英文四选一，**尚无独立人类专家复核**。

Qwen 均为 Q8_0，temperature=1，三轮 seed 为 101／202／303。轮次同时
轮换选项位置，因此不能把跨轮变化单独归因于随机采样或位置偏好。
思考到预算后继续生成答案，总生成上限为预算 + 128；Jev 使用原生 Choice API。

发布范围是在观察实验结果后确定的，属于探索性报告，不宣称盲测预注册。
所保留条件的全部题目、答案和三轮记录均未改动。发布协议是对执行条件和
保留范围的整理，原始协议／配置哈希保存在 [release_provenance.json](data/release_provenance.json)。

## 如何复算

Python 3.10+；计分不需要第三方依赖。

```sh
python -m pip install -e '.[plots]'
python -m unittest discover -s tests -v
python -m jf100.budget_report v0.2-budget --from-public
python scripts/plot_budget_results.py v0.2-budget
```

以上步骤无需密钥或模型，即可从公开逐题结果重新计算总分、置信区间和图表。
重新调用模型需要安装对应 Q8 模型、支持思考预算与 LP 的 llama-server，
并设置 `JEV_KEY`；完整命令见[英文说明](README.md#inspect-and-reproduce)。
实验使用 Apple M5 Max／128 GiB。模型和后端指纹随结果提供。

## 保留了哪些数据

公开的 [outcomes.jsonl](results/v0.2-budget/outcomes.jsonl) 包含每次计分、输入哈希、
token 数、答案字母的 LP／概率、Jev 置信度等。输入可由题集和轮次重新构造。

完整输入、thinking、最终答案和所有 token 的 LP／前五候选保留在本地
`runs/`。为避免仓库过大，不直接提交 Git；可以用 `scripts/export_raw.py`
生成带哈希的压缩发布附件。完整 3,000 条记录已随 [v0.2.0 发布](https://github.com/softpudding/jev-frontier-100/releases/tag/v0.2.0)提供下载与校验清单。记录结构见 [DATA_LAYOUT.md](docs/DATA_LAYOUT.md)。

Qwen 的答案 token 概率没有在 A/B/C/D 间重新归一化，不等于“答案正确率”；
Jev 置信度的定义也不同。因此[可靠性图](results/v0.2-budget/confidence.png)和 Brier 分数
只作探索性诊断，需同时看可对齐记录数和实际正确性。

MIT 许可。欢迎指出有歧义的题目或贡献更难、经过独立复核的题目。
