# 大模型面试要点

Transformer 使用自注意力机制建模序列中不同 token 的依赖关系。Attention 的计算通常写作 softmax(QK^T/sqrt(d_k))V。温度参数影响采样随机性，temperature 越高输出越发散。

生产系统需要关注上下文窗口、Token 成本、延迟、重试和安全。提示词应明确角色、约束和输出格式，不能把模型常识伪装成知识库事实。
