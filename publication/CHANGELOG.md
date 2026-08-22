# 📝 NSEH 更新日志 / Changelog

> 本文件从 `readme.md` 迁移至 **publication** 板块，作为项目的 Release Notes。
> Moved from `readme.md` to the **publication** section as the project's Release Notes.

---

## v5.3 最新 / Latest

- 🧩 **扩展至 20 个组合优化问题情景**：新增 15 个（Bin Packing / Graph Coloring / JSP / Set Cover / Vertex Cover / mTSP / VRPTW / Orienteering / Steiner Tree / MaxClique / SMTWT / Parallel Machine / QAP / k-Center / Partition），每个含数据集、标准解、评估、CLI、可视化
  - **Expanded to 20 combinatorial optimization problem scenarios**: 15 new ones added, each with datasets, reference solutions, evaluators, CLI, and visualization
- 🛡️ **启发式特征提取自检**（`core/prompt_template.py`）：标准解析失败时四层鲁棒回退（L1 花括号块 → L2 全文方括号 → L3 标签行 → L4 短语兜底），保证特征非空
  - **Heuristic feature extraction self-check**: four-level robust fallback (L1 brace block → L2 brackets → L3 label line → L4 phrase fallback) when standard parsing fails
- 🤖 **LLM 预设更新至 2026-08 最新**：DeepSeek V4 / GPT-5.6 / Claude 5 / Gemini 3.x / Qwen3.8 / GLM-5.3 / Kimi K3 等 28 个预设，默认模型改为 DeepSeek V4 Flash
  - **LLM presets updated to 2026-08 latest**: 28 presets; default model is now DeepSeek V4 Flash
- 📖 **README 更新**：20 个问题情景全部收录（折叠展示），目录树同步
  - **README updated**: all 20 problem scenarios documented (collapsible), project tree synced

---

## v2.5 更新 / v2.5

- 🏆 **排行榜系统**：独立排名页面（`/rank`），展示各用户最优适应度
  - **Leaderboard system**: dedicated ranking page (`/rank`) showing each user's best fitness
- 🧠 **分层标签记忆系统**（`core/tag_memory.py`）：场景感知的标签分类树，积极/消极记忆分层归档，告别暴力遗忘
  - **Hierarchical tag memory system** (`core/tag_memory.py`): scenario-aware tag classification tree with tiered archiving of positive/negative memory
- ⚙️ **配置缓存**（`.config_cache.json`）：前进化设置自动保存/恢复
  - **Config cache** (`.config_cache.json`): evolution settings are auto-saved/restored
- 🎨 **UI 重构**：暖橙色调统一，移除赛博朋克配色，保留玻璃拟态装饰效果
  - **UI redesign**: unified warm-amber palette, cyberpunk colors removed, glassmorphism kept
- 🔄 **实时进化进度 API**：前端轮询展示各代种群数据
  - **Real-time evolution progress API**: frontend polls and displays per-generation population data
- 📂 **存档载入**：加载历史进化记录继续实验
  - **Snapshot loading**: resume experiments from historical evolution records
- 📝 **Prompt 模板编辑**：进化过程中可修改 LLM 提示词
  - **Prompt template editing**: modify LLM prompts during evolution
- 💻 **LLM 预设切换**：支持 DeepSeek / GPT / Claude 等多模型
  - **LLM preset switching**: DeepSeek / GPT / Claude and more
- 🌗 **明暗主题切换**
  - **Light/dark theme toggle**
- 🌐 **中英双语界面**（v5.1）：右上角语言切换按钮，界面文字与预设 Prompt 模板同步切换（中文/English）
  - **Bilingual UI (v5.1)**: language toggle in the top-right corner; UI text and preset prompt templates switch between Chinese/English

---

## v2.1 更新

### 🧑‍🤝‍🧑 角色系统 / Role System

新增管理员/普通用户两级用户体系：

- **管理员**（账号：000000000，密码：142857）：登录后可见「⚙️ 管理后台」按钮，点击弹出用户列表及实验记录
  - **Admin** (account: 000000000, password: 142857): sees the "⚙️ Admin Panel" button after login, showing the user list and experiment records
- **普通用户**：正常使用进化功能，查看个人实验历史和排行榜
  - **Regular users**: use evolution features, view personal history and leaderboard
- 管理员账号首次启动时通过 `INSERT OR IGNORE` 自动创建
  - The admin account is auto-created on first startup via `INSERT OR IGNORE`

### 🔒 数据库增强 / Database Enhancements

- 用户表新增 `role` 列
  - New `role` column in the users table
- 向后兼容：自动 `ALTER TABLE` 为旧表添加 role 列
  - Backward compatible: auto `ALTER TABLE` to add the role column to old tables
- 登录 API 返回用户角色信息，前端根据角色显示管理按钮
  - The login API returns role info; the frontend shows the admin button based on role

---

## v2.0 及更早 / v2.0 and earlier

历史版本记录见 git 提交历史：
For earlier versions, see the git commit history:
`git log --oneline`
