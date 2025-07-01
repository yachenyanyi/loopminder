
```markdown
# LoopMinder 🔄🤖

**多智能体自动化项目构建与文档生成系统**  
支持灵活接入多种AI模型，实现本地项目设计、代码生成和文档自动化编写。

![Demo](https://via.placeholder.com/800x400?text=LoopMinder+Demo) <!-- 建议替换为实际项目截图 -->

## ✨ 核心功能

### 🗣️ 简单对话模式
- **轻量级交互**：处理文档编写、代码片段生成等任务
- **低性能需求**：兼容 Ollama 等本地模型
- **适用场景**：快速问答/小规模内容生成

### 🏗️ 项目构建模式
- **标准化流程**：全生命周期项目构建（设计→开发→文档）
- **高性能要求**：推荐使用 128K 上下文窗口的API模型
- **输出管理**：
  - 生成文档自动保存至 `/DOC` 目录
  - 临时文件存储于 `/workplace` 共享工作区

## 🛠️ 安装与使用

### 环境要求
- Python 3.10(推荐)




## ⚙️ 模型配置

在 `model/model.py` 中添加您的模型：

```
例如：
os.environ["DEEPSEEK_API_KEY"]="<api_key>"
<api_key>换成你的deepseek api密钥
在"https://platform.deepseek.com"注册获得
deepseek_model=ChatDeepSeek(model="deepseek-chat",#更换模型deepseek-response
                            temperature=1.5)
default_model=ollam_model#默认ollama
切换至deepseek
default_model=deepseek_model
```



## ⚠️ 已知问题
1. **项目构建模式**：
   - 可能意外中断（正在优化稳定性）
   - 生成的项目路径可能存在异常

2. **工作区管理**：
   - 所有对话共享 `/workplace` 目录
   - 需手动清理旧文件避免冲突

## 🚧 待实现功能
- [ ] 任务隔离（独立工作区）
- [ ] 项目路径生成优化
- [ ] 自动清理过期文件
- [ ] 更便捷的模型切换方式

## 🤝 参与贡献
欢迎提交 Issue 或 PR：


## 📜 开源协议
[GNU GPL-3.0](LICENSE) © 2025 [YachenYanyi](https://github.com/yachenyanyi)



