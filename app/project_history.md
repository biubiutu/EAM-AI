# AI-EAM 智能设备资产管理系统 - 项目开发全记录

> 本文档记录了从项目初始到现在的所有问答、决策和开发历程。
> 创建日期：2026-06-05

---

## 目录

1. [项目概述](#1-项目概述)
2. [第一阶段：项目初始化与架构搭建](#2-第一阶段项目初始化与架构搭建)
3. [第二阶段：核心功能开发](#3-第二阶段核心功能开发)
4. [第三阶段：多角色功能完善](#4-第三阶段多角色功能完善)
5. [第四阶段：AI智能体集成](#5-第四阶段ai智能体集成)
6. [第五阶段：存储与数据优化](#6-第五阶段存储与数据优化)
7. [第六阶段：全面功能增强（最新）](#7-第六阶段全面功能增强最新)
8. [技术架构总结](#8-技术架构总结)
9. [附录：API 端点清单](#9-附录api-端点清单)

---

## 1. 项目概述

### 1.1 项目目标
构建一个智能设备资产管理系统（AI-EAM），覆盖设备维修、备件管理、采购管理、人员调度等全流程，集成 AI 大模型能力实现智能诊断、语音识别、智能审批、自动报告生成等功能。

### 1.2 技术栈
| 层次 | 技术选型 |
|------|---------|
| 前端 | 原生 HTML/CSS/JavaScript（single-page application） |
| 后端 | Python FastAPI |
| 数据库 | MySQL (SQLAlchemy async) |
| 向量数据库 | Milvus |
| 对象存储 | MinIO |
| 图数据库 | Neo4j |
| 缓存 | Redis |
| AI 模型 | DeepSeek / Ollama / SiliconFlow |
| 语音识别 | Whisper |

### 1.3 用户角色
| 角色 | 标识 | 主要职责 |
|------|------|---------|
| 管理员 | admin | 系统管理、用户权限、全功能访问 |
| 工程师 | engineer | 故障诊断、维修作业、语音转文字、技能考核 |
| 主管 | supervisor | 备件管理、工程师调派、调拨评估 |
| 采购员 | purchaser | 报价单管理、合同审查、供应商管理 |
| 领导 | leader | 数据看板、数据洞察、LCC分析、审批决策 |
| 访客 | guest | 个人信息查看 |

---

## 2. 第一阶段：项目初始化与架构搭建

### 2.1 项目初始化

**Q: 项目的基础架构怎么设计？**
**A:** 采用前后端分离架构：
- 前端单页应用（main.html），通过 JavaScript 动态渲染页面
- 后端 FastAPI 框架，按角色划分路由模块
- 数据库采用 MySQL + Milvus 向量库 + MinIO 对象存储

**Q: 如何组织后端代码？**
**A:** 
```
app/
├── api/v1/           # API 路由（按角色分模块）
│   ├── common/       # 公共（登录、注册、上传）
│   ├── engineer/     # 工程师
│   ├── leader/       # 领导
│   ├── purchaser/    # 采购员
│   └── supervisor/   # 主管
├── config/           # 配置
├── core/             # 核心（数据库、安全、异常处理）
├── models/           # SQLAlchemy 模型
├── schemas/          # Pydantic 模型
├── services/         # 业务逻辑 + AI 服务
└── utils/            # 工具类（MinIO、Milvus、AI客户端）
```

### 2.2 数据库设计

**Q: 数据库表怎么设计？**
**A:** 设计了以下核心表：
- `users` - 用户表（支持多角色）
- `engineer_dispatches` - 调派记录表
- `approval_records` - 审批记录表
- `work_orders` - 工单表
- `equipment` - 设备表
- `purchase_orders` - 采购单表
- `spare_parts` - 备件表

**Q: 用户角色如何实现？**
**A:** 使用枚举 `UserRole` 定义角色（admin/engineer/supervisor/purchaser/leader/guest），通过 JWT token 存储角色信息，用 `RoleChecker` 依赖注入控制 API 访问权限。

### 2.3 安全架构

**Q: 权限控制怎么实现？**
**A:** 
- JWT 身份认证（token 存储 username, role, user_id）
- `RoleChecker` 类实现角色权限验证
- 后端每个路由通过 `Depends(allow_xxx)` 控制访问
- 前端根据 `ROLE_CONFIG` 动态渲染导航菜单

---

## 3. 第二阶段：核心功能开发

### 3.1 登录注册

**Q: 登录注册怎么实现？**
**A:**
- 前端：`renderLogin()` / `renderRegister()` 渲染登录/注册页面
- 后端：`POST /api/v1/common/auth/login` 和 `POST /api/v1/common/auth/register`
- 密码使用哈希存储，登录返回 JWT token
- token 存储在 localStorage，每次请求自动携带

### 3.2 数据看板（领导）

**Q: 领导数据看板需要什么功能？**
**A:**
- `renderLeaderDashboard()` - 设备统计概览（设备总数、维修单数、采购总额）
- `doDashQuery()` - 自然语言查询（Text2SQL），将中文问题转为 SQL 查询
- `doInsight()` - AI 数据洞察分析

### 3.3 AI 故障诊断（工程师）

**Q: 故障诊断怎么实现？**
**A:**
- 前端输入设备ID + 故障描述
- 后端调用 AI 大模型分析故障原因、推荐维修方案
- 结合知识库（RAG）检索相关维修手册
- 输出结构化诊断结果

### 3.4 语音转文字

**Q: 语音识别如何集成？**
**A:**
- 使用 Whisper 模型进行语音识别
- 前端上传音频文件 → 后端 Whisper 转文字 → 返回识别结果
- 支持 MP3/WAV/M4A 格式
- 文件同时上传到 MinIO 存储

---

## 4. 第三阶段：多角色功能完善

### 4.1 采购管理模块

**Q: 采购报价单处理流程？**
**A:**
1. 上传报价单文件（PDF/Excel）
2. 存储到 MinIO（prefix: `quotations/`）
3. AI 提取报价信息（商品、价格、数量、供应商）
4. 比价分析：对比多供应商报价，生成推荐方案

**Q: 合同审查怎么实现？**
**A:**
- 文本审查：直接输入合同文本，AI 识别风险条款
- 文件审查：上传合同文件（PDF/Word/TXT）
- 审查结果包括风险等级、风险条款、修改建议
- 文件自动存储到 MinIO（prefix: `contracts/`）

### 4.2 供应商管理

**Q: 供应商管理包含哪些功能？**
**A:**
- 供应商风险评估：AI 分析供应商履约风险
- 供应商推荐：根据备件需求推荐合适供应商
- 价格趋势分析：分析历史价格走势

### 4.3 备件管理（主管）

**Q: 主管的备件管理功能？**
**A:**
- BOM 检查：检查设备 BOM 清单完整性
- 申购分析：AI 分析备件申购需求合理性
- 调拨评估：评估备件调拨的可行性

### 4.4 LCC 全生命周期成本分析

**Q: LCC 分析怎么做？**
**A:**
- 输入设备ID和年份
- AI 综合分析采购成本、维护成本、能耗成本、停机损失
- 输出全生命周期成本报告和改进建议

---

## 5. 第四阶段：AI智能体集成

### 5.1 审批决策辅助（领导）

**Q: AI审批建议怎么实现？**
**A:**
- 加载待审批列表
- 领导选择审批事项，AI 生成审批建议（同意/拒绝及理由）
- 领导确认后执行审批操作

### 5.2 工程师推荐（主管）

**Q: 如何推荐最佳工程师？**
**A:**
- 根据维修地点计算距离
- 根据工程师技能评分（电气、机械、液压等多维度）
- 综合评分公式：`avg_skill * 0.4 - distance * 0.6`
- 按评分排序推荐

### 5.3 技能考核（工程师）

**Q: 技能考核系统怎么设计？**
**A:**
- 选择考核类型（虚拟故障诊断/维修对话）
- AI 根据技能水平生成故障场景和题目
- 学员逐题作答，AI 实时评估正确性
- 提交全部答案后给出综合评分和改进建议
- 生成技能雷达图

### 5.4 物联网预测性维护

**Q: IoT 数据分析做什么？**
**A:**
- 输入设备ID和传感器数据（温度、振动等）
- AI 分析设备健康状态
- 预测可能发生的故障
- 建议维护时间窗口

---

## 6. 第五阶段：存储与数据优化

### 6.1 文件存储策略

**Q: 上传文件存到哪里？**
**A:** 所有文件统一存储到 MinIO，按类型分类：
- 维修手册 → `knowledge-base/manuals/`
- 合同文件 → `knowledge-base/contracts/`
- 报价单 → `knowledge-base/quotations/`
- 语音文件 → `knowledge-base/audio/`
- 通用文件 → 默认 bucket

**Q: 知识库搜索怎么实现？**
**A:**
1. 上传文档到 MinIO
2. 切片后向量化存入 Milvus
3. 搜索时：用户问题 → 向量化 → Milvus 相似度检索 → 返回匹配片段
4. 支持 PDF、Word、TXT、图片等多种格式

### 6.2 MinIO 接入

**Q: MinIO 客户端封装了什么功能？**
**A:**
- `upload_file()` - 上传文件（自动生成唯一文件名）
- `get_file_url()` - 获取预签名下载 URL
- `download_file()` - 下载文件内容
- `list_files()` - 列出指定前缀的文件列表（后新增）

**Q: MinIO 配置参数？**
**A:**
```env
MINIO_ENDPOINT=127.0.0.1:9100
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=vanna-training-data
KB_BUCKET_NAME=knowledge-base
```

---

## 7. 第六阶段：全面功能增强（最新）

> 时间：2026-06-05

### 7.1 管理员权限扩展

**Q: 管理员为什么只看到了领导权限的地方，应该看全部人的？**
**A:** 修复了 `ROLE_CONFIG.admin.pages`，为管理员配置了所有角色的页面入口：
- 系统管理（用户角色权限）
- 数据与决策（数据看板、数据洞察、LCC分析、审批决策辅助、AI审批）
- 故障诊断（AI故障诊断、知识库搜索、故障案例）
- 维修作业（上传维修手册、语音转文字、图片分析、生成报告）
- 技能与监控（技能考核、IoT分析）
- 备件管理（BOM检查、申购分析、调拨评估）
- 人员调度（工程师调派）
- 采购管理（上传报价单、比价分析、合同审查、合同查询）
- 供应商管理（风险评估、供应商推荐、价格趋势）

### 7.2 领导 422 错误修复

**Q: 领导的所有查询全部报422？**
**A:** 原因及修复：
1. `doDashQuery()` 发送字段名为 `query`，后端 `Text2SQLRequest` 期望 `question` → 修复为 `{question: q}`
2. `doInsight()` 调用错误 endpoint（`/query`），应调用 `/insight` → 修复 URL 和参数

### 7.3 AI审批改为勾选模式

**Q: 我不要审批事项ID，直接在每个事件前面勾选？**
**A:** 重新设计审批界面：
- 废除审批事项ID输入框
- 每行待审批事项前增加 checkbox
- 新增全选/取消全选功能
- 批量同意/批量拒绝按钮
- 按顺序逐个执行审批操作，显示成功/失败统计

### 7.4 在线语音输入

**Q: 语音转文字可以在线语音输入，不用文件？**
**A:** 集成浏览器 `MediaRecorder` API：
- 新增"开始录音/停止录音"按钮
- 点击开始 → 请求麦克风权限 → 录制音频
- 实时计时显示（MM:SS）
- 停止录制 → 自动上传 WebM 音频 → AI 识别 → 显示结果
- 保留原有文件上传方式作为备选

### 7.5 技能考核成绩和正确答案

**Q: 提交完答案要能看到自己成绩和正确答案？**
**A:** 改进方案：
- 前端 `submitExam()` 改为调用 `/exam/submit`（之前错误地调用了 `/exam/answer`）
- 后端 `submit_exam()` 不再使用简单启发式（`len>10`），改用 `exam_service.evaluate_answer()` AI 逐题评估
- 返回数据包含每题：用户答案、参考答案、得分、反馈意见
- 前端清晰展示每题的评分详情

### 7.6 采购合同查询

**Q: 新增合同查询功能，直接去MinIO查到数据？**
**A:** 
- MinIO 客户端新增 `list_files()` 方法
- 后端新增 `GET /purchaser/contract/list`（列出合同文件）
- 后端新增 `GET /purchaser/contract/download-url`（获取下载链接）
- 前端新增"合同查询"页面，表格展示文件名、大小、时间，支持下载

### 7.7 调派成本智能估算

**Q: 主管工程师委派，输入地点，调用智能体判断成本？**
**A:**
- 后端新增 `POST /supervisor/dispatch/cost-estimate` 端点
- AI 智能体根据地点描述估算距离和交通费用
- 考虑时间段因素（晚上/郊区费用上浮）
- 前端新增"💰 AI估算成本与距离"按钮
- 结果自动填充到距离和成本输入框
- 数据传给 `create_dispatch` 存入数据库

---

## 8. 技术架构总结

### 8.1 前端架构

```
main.html (单页应用)
├── ROLE_CONFIG      # 角色菜单配置
├── PAGE_RENDER      # 页面路由映射
├── 通用函数
│   ├── apiGet/apiPost # HTTP 请求封装
│   ├── showTable      # 表格渲染
│   ├── showResult     # 结果展示
│   └── renderFileUpload # 文件上传组件
├── 角色功能函数
│   ├── 管理员: renderAdminUsers, loadRolePerms
│   ├── 工程师: doDiagnosis, toggleVoiceRecord, submitExam, ...
│   ├── 领导: doDashQuery, doInsight, doBatchApprove, ...
│   ├── 采购员: doContractReview, loadContractList, doPriceCompare, ...
│   └── 主管: doEstimateCost, doRecommend, doCreateDispatch, ...
└── 登录/注册: renderLogin, renderRegister
```

### 8.2 后端请求流

```
HTTP Request
  → FastAPI Router (按角色/功能分模块)
    → RoleChecker (权限验证)
      → BaseRouter (统一响应格式)
        → Service Layer (业务逻辑 + AI调用)
          → Utils (MinIO/Milvus/DB)
            → Response (统一 BaseResponse)
```

### 8.3 AI 能力清单

| 能力 | 模型/服务 | 用途 |
|------|-----------|------|
| 文本生成 | DeepSeek / Qwen | 故障诊断、报告生成、审批建议 |
| 语音识别 | Whisper | 语音转文字 |
| 图片分析 | 多模态模型 | 故障图片分析 |
| 向量嵌入 | BGE / nomic | 知识库检索 |
| Text2SQL | DeepSeek / Qwen | 自然语言查数据库 |
| 代码生成 | DeepSeek | 维修代码生成 |

### 8.4 数据存储架构

```
MySQL - 业务数据（用户、工单、调派、审批）
  ├── users
  ├── engineer_dispatches
  ├── approval_records
  └── work_orders

Milvus - 向量数据（知识库片段、故障案例）
  ├── equipment_knowledge (维修手册向量)
  └── fault_cases (故障案例向量)

MinIO - 文件存储
  ├── knowledge-base/
  │   ├── manuals/     # 维修手册
  │   ├── contracts/   # 合同文件
  │   ├── quotations/  # 报价单
  │   └── audio/       # 语音文件
  └── vanna-training-data/  # 通用文件

Neo4j - 图数据（设备关系图谱）
Redis - 缓存（会话、临时数据）
```

---

## 9. 附录：API 端点清单

### 公共
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/common/auth/login` | 登录 |
| POST | `/api/v1/common/auth/register` | 注册 |
| POST | `/api/v1/common/upload/file` | 通用文件上传 |

### 工程师
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/engineer/diagnosis/analyze` | AI故障诊断 |
| POST | `/api/v1/engineer/knowledge/search` | 知识库搜索 |
| POST | `/api/v1/engineer/knowledge/upload-manual` | 上传维修手册 |
| POST | `/api/v1/engineer/knowledge/ingest-case` | 录入故障案例 |
| POST | `/api/v1/engineer/knowledge/search-case` | 搜索故障案例 |
| POST | `/api/v1/engineer/work-order/speech-to-text` | 语音转文字 |
| POST | `/api/v1/engineer/work-order/analyze-image` | 图片分析 |
| POST | `/api/v1/engineer/work-order/generate-report` | 生成维修报告 |
| POST | `/api/v1/engineer/exam/start` | 开始考核 |
| POST | `/api/v1/engineer/exam/answer` | 提交单题答案 |
| POST | `/api/v1/engineer/exam/submit` | 批量提交评分 |
| POST | `/api/v1/engineer/exam/skill-radar` | 技能雷达图 |
| POST | `/api/v1/engineer/predictive/iot-analyze` | IoT分析预测 |

### 领导
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/leader/dashboard/query` | Text2SQL查询 |
| POST | `/api/v1/leader/dashboard/insight` | 数据洞察 |
| GET | `/api/v1/leader/dashboard/approval-list` | 待审批列表 |
| POST | `/api/v1/leader/dashboard/approval-action` | 审批操作 |
| POST | `/api/v1/leader/lcc/analyze` | LCC成本分析 |

### 采购员
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/purchaser/quotation/upload` | 上传报价单（存MinIO） |
| POST | `/api/v1/purchaser/quotation/compare` | 比价分析 |
| POST | `/api/v1/purchaser/contract/review` | 合同文本审查 |
| POST | `/api/v1/purchaser/contract/review-file` | 合同文件审查（存MinIO） |
| **GET** | **`/api/v1/purchaser/contract/list`** | **合同列表查询** ⭐新增 |
| **GET** | **`/api/v1/purchaser/contract/download-url`** | **合同下载链接** ⭐新增 |
| POST | `/api/v1/purchaser/supplier/risk-check` | 供应商风险评估 |
| POST | `/api/v1/purchaser/supplier/recommend` | 供应商推荐 |
| POST | `/api/v1/purchaser/supplier/price-trend` | 价格趋势分析 |

### 主管
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/supervisor/dispatch/create` | 创建调派 |
| GET | `/api/v1/supervisor/dispatch/list` | 调派记录 |
| GET | `/api/v1/supervisor/dispatch/engineers` | 工程师列表 |
| POST | `/api/v1/supervisor/dispatch/recommend` | AI推荐工程师 |
| **POST** | **`/api/v1/supervisor/dispatch/cost-estimate`** | **成本距离估算** ⭐新增 |
| POST | `/api/v1/supervisor/dispatch/complete/{id}` | 完成调派 |
| POST | `/api/v1/supervisor/equipment/bom-check` | BOM检查 |
| POST | `/api/v1/supervisor/requisition/analyze` | 申购分析 |
| POST | `/api/v1/supervisor/sharing/transfer-evaluate` | 调拨评估 |

---

## 10. 第七阶段：数据库中文化与数据迁移（2026-06-05）

### 10.1 用户请求
- 将所有数据库表名改为中文
- 将所有表字段名改为中文
- 将旧表数据迁移到新中文表
- 删除旧英文表

### 10.2 修改内容

#### 模型层全面中文化
- **base.py**: 基础字段 `id` -> `ID`, `created_at` -> `创建时间`, `updated_at` -> `更新时间`
- **user.py**: `users` -> `用户`, `skill_records` -> `技能记录`, `exam_records` -> `考核记录`
- **equipment.py**: `equipments` -> `设备`, `bom_items` -> `BOM清单`
- **work_order.py**: `work_orders` -> `工单`, `inspection_records` -> `巡检记录`, `maintenance_plans` -> `维护计划`
- **spare_part.py**: `spare_parts` -> `备件`, `warehouses` -> `仓库`, `inventory_records` -> `库存记录`, `requisitions` -> `申购单`, `transfer_orders` -> `调拨单`, `stagnant_alerts` -> `呆滞预警`
- **purchase.py**: `suppliers` -> `供应商`, `supplier_categories` -> `供应商品类`, `quotations` -> `报价单`, `price_comparisons` -> `比价记录`, `contracts` -> `合同`, `supplier_risk_alerts` -> `供应商风险预警`, `commodity_prices` -> `大宗商品价格`, `sourcing_recommendations` -> `寻源推荐`
- **approval.py**: `approval_records` -> `审批记录`, `cost_analyses` -> `成本分析`
- **dispatch.py**: `engineer_dispatches` -> `工程师调派`

#### 数据迁移
- 创建 `app/migrate_data.py` 迁移脚本
- 按依赖顺序迁移（无外键表先，有外键表后）
- 迁移前临时关闭外键检查 `SET FOREIGN_KEY_CHECKS=0`
- 25张表全部迁移成功，共迁移约 100+ 条记录

#### 删除旧表
- 创建 `app/drop_old_tables.py` 脚本
- 成功删除 25 张旧英文表

### 10.3 遇到的问题与解决
1. **外键约束错误**: 新中文表之间存在外键关联，插入顺序错误导致失败
   - 解决：按依赖拓扑排序，先插入无外键的表（用户、设备、备件、仓库、供应商），再插入有外键的表
2. **字段名映射错误**: `id` 列在新表中仍叫 `id`（基础类定义），但 COLUMN_MAP 中映射为 `ID`
   - 解决：修正基础类，保持 `id` 不变，其他字段改为中文
3. **创建时间/更新时间默认值问题**: 中文表创建后插入数据时时间字段为 NULL
   - 解决：修改模型使用 `server_default=func.now()` 和 `server_onupdate=func.now()`

---

## 11. 第八阶段：供应商风险评估模拟数据方案（2026-06-05）

### 11.1 问题现象
用户在采购员角色的"供应商风险评估"页面输入供应商信息后，返回结果为：
```
【alerts】[]
【assessment】{}
```

### 11.2 问题原因
`app/services/ai_services/supplier_risk_agent.py` 原实现调用 AI 大模型分析供应商风险，但：
1. AI 没有接入实时新闻、工商、舆情等外部数据源
2. 用户仅传了 `supplier_id` 和 `supplier_name`，信息太少
3. AI 无法真实查询，只能"猜测"，通常会返回空数组表示"未发现风险"

### 11.3 解决方案（方案2：模拟数据）
修改 `supplier_risk_agent.py`，不再调用 AI 大模型，改为基于供应商名称生成确定性的模拟风险数据：

- **8种风险模板**：交付延迟、质量抽检不合格、财务状况异常、原材料价格波动、单一供应源依赖、信用评级下调、环保合规风险、地缘政治运输风险
- **确定性生成**：使用 `hashlib.md5(supplier_name)` 作为随机种子，确保同一供应商每次评估结果一致
- **综合评估**：根据风险严重程度自动判定 overall_risk_level（low/medium/high）、是否启动备选供应商、应急措施和监控建议
- **时间戳**：每条风险带 `detected_at` 字段，模拟 1-30 天内检测到

### 11.4 代码变更
- **修改**: `app/services/ai_services/supplier_risk_agent.py`
  - 移除 `ai_client` 依赖
  - 新增 `RISK_TEMPLATES` 列表（8条模拟风险）
  - 新增 `_get_seed()` / `_generate_demo_alerts()` / `_generate_demo_assessment()` 方法
  - `monitor_supplier_risks()` 和 `assess_risks()` 改为同步生成逻辑

---

## 12. 第九阶段：删除旧表与会话记录归档（2026-06-05）

### 12.1 删除旧英文表
**用户请求：** 删除所有旧英文表

**操作：**
- 创建 `app/drop_old_tables.py` 脚本
- 先执行 `SET FOREIGN_KEY_CHECKS=0` 解除外键约束
- 循环删除 25 张旧英文表（users, skill_records, equipments 等）
- 删除完成后重新开启外键检查
- 验证确认数据库中仅保留 25 张中文表

### 12.2 会话归档记录
**用户请求：** 将本软件所有历史问答持续写入 project_history.md，不论是否与当前模型相关

**后续更新策略：**
- 每个开发阶段完成后追加记录到 project_history.md
- 记录内容包括：用户请求、问题原因、解决方案、代码变更、遇到的问题与修复
- 保持文档结构一致，按阶段编号递增
- 文件末尾标注最后更新日期

---

## 13. 第十阶段：报价单上传速度优化与多文件支持（2026-06-05）

### 13.1 问题现象
1. 报价单上传图片（即使 100KB）一直转圈，非常慢
2. 通用文件上传也慢
3. 报价单一次只能上传一个文件，无法批量比价

### 13.2 问题原因
1. **AI Vision 调用超时**：之前修改的 `chat_with_image()` 尝试将图片 base64 发给 DeepSeek。但 DeepSeek 标准模型不支持 vision 多模态，API 请求等 120 秒超时后才抛异常降级，导致每次上传图片都要等 2 分钟
2. **单文件限制**：前端 `<input type="file">` 没有 `multiple` 属性，后端也只接受单文件 `UploadFile`

### 13.3 解决方案
**速度优化：**
- 图片上传不再调用 AI vision（当前模型不支持），直接存 MinIO 后立即返回
- 前端提示"图片已存储，文本提取请使用 PDF/Excel 格式"
- 移除 `chat_with_image` 在 quotation 中的调用

**多文件支持：**
- 后端 `quotation.py`：`upload_quotation` → `upload_quotations`，接收 `list[UploadFile]`，每个文件独立处理
- 后端 `upload.py`：同理改为多文件接收
- 前端 `renderFileUpload`：新增 `multiple` 选项，支持多选文件
- FormData 中每个文件以 `files` 字段发送

### 13.4 修改的文件
| 文件 | 变更类型 | 说明 |
|------|----------|------|
| `app/api/v1/purchaser/quotation.py` | 修改 | 改为多文件上传，图片跳过AI vision直接存 |
| `app/api/v1/common/upload.py` | 修改 | 改为多文件上传 |
| `frontend/main.html` | 修改 | renderFileUpload 支持多选，报价单+通用上传均启用多文件 |

---

## 14. 第十一阶段：接入 Ollama 本地视觉模型识别报价单图片（2026-06-05）

### 14.1 背景
用户询问 Ollama 是否有视觉模型可用，经检查原本没有。用户主动拉取了 `qwen3.5:0.8B`（1.0GB），该模型具备 vision 能力。

### 14.2 修改内容
**`app/utils/ai_client.py`**：
- 新增 `_get_ollama_client()` 方法，创建连接到 `OLLAMA_BASE_URL/v1` 的 OpenAI 兼容客户端
- 新增 `chat_with_image_ollama()` 方法，将图片 base64 编码后发送给 Ollama 的 qwen3.5:0.8B 视觉模型识别
- 保留原有的 `chat_with_image()` 方法（兼容外部 API 调用）

**`app/api/v1/purchaser/quotation.py`**：
- 图片处理逻辑改为调用 `ai_client.chat_with_image_ollama()` 提取报价单信息
- 识别成功后返回结构化 JSON（备件名称、规格、单价、数量等）
- 识别失败时返回原始文本供用户查看

### 14.3 文件变更
| 文件 | 变更 |
|------|------|
| `app/utils/ai_client.py` | 新增 `_get_ollama_client()`、`chat_with_image_ollama()` |
| `app/api/v1/purchaser/quotation.py` | 图片走 Ollama 视觉识别 |

---

## 15. 第十二阶段：修复数据库字段中文名导致登录崩溃（2026-06-05）

### 15.1 问题
用户反馈"登录不了，密码没改"，postman 测试 login 接口返回 500 错误。

### 15.2 原因
早前数据库表/字段全部改成了中文（如`用户名`、`密码哈希`、`角色`等），但代码中多处仍使用英文字段名：
- `User.username` → 应为 `User.用户名`
- `user.password_hash` → 应为 `user.密码哈希`
- `user.is_active` → 应为 `user.是否激活`
- `user.role` → 应为 `user.角色`
- 等等

登录时触发 `AttributeError: type object 'User' has no attribute 'username'`，导致 500。

### 15.3 修复文件
| 文件 | 变更 |
|------|------|
| `app/api/v1/common/auth.py` | 全部 User 字段引用改为中文列名 |
| `app/api/v1/supervisor/dispatch.py` | `User.role` / `User.is_active` → `User.角色` / `User.是否激活` |

---

## 16. 第十三阶段：修复 Ollama CPU 视觉模型超时，接入 SiliconFlow 云端视觉 API（2026-06-05）

### 16.1 问题
报价单上传图片后返回 `"解析失败: Request timed out"`，用户询问是模型不能解析还是没识别出内容。

### 16.2 原因
- 机器**无 GPU**，`qwen3.5:0.8B` 跑在 **100% CPU**
- CPU 处理图片推理极慢，一个 129KB 的 PNG 需要几分钟，超过 120 秒超时
- `ollama ps` 显示三个模型均 `100% CPU`，无 GPU 加速

### 16.3 解决方案
**`ai_client.py`**：
- 新增 `_get_siliconflow_client()`，连接 SiliconFlow 云端 API（60 秒超时）
- 新增 `_chat_with_image_siliconflow()`，使用 `Qwen/Qwen2.5-VL-7B-Instruct`（云端 GPU 模型）
- 新增 `chat_with_image()` 统一入口：**优先走 SiliconFlow → Ollama 降级**
- 公有方法 `chat_with_image()` 自动处理两个后端的异常和 fallback

**`quotation.py`**：
- 图片调 `ai_client.chat_with_image()` 替换原来的 `chat_with_image_ollama()`

### 16.4 效果
- SiliconFlow 云端 GPU 处理图片通常在 **3-10 秒内**返回结果
- 如果云端 API 不可用，自动降级到本地 Ollama 模型
- 用户无需关心后端选择

### 16.5 修改文件
| 文件 | 变更 |
|------|------|
| `app/utils/ai_client.py` | 新增 SiliconFlow 视觉客户端、`chat_with_image()` 统一入口 |
| `app/api/v1/purchaser/quotation.py` | 改用 `chat_with_image()` |

---

## 17. 第十四阶段：修正 MinIO 桶名、上传添加取消按钮、确认 Milvus 配置（2026-06-05）

### 17.1 需求
1. MinIO 的桶名实际为 `xiangmu`（项目），非默认的 `knowledge-base`
2. 上传报价单/Milvus 向量库名称为 `AI_EAM`
3. 前端文件上传需要支持取消操作

### 17.2 修改

**MinIO 桶名修正：**
- `.env`：`KB_BUCKET_NAME="knowledge-base"` → `"xiangmu"`
- `app/config/settings.py`：默认值同步改为 `"xiangmu"`

**Milvus 配置确认：**
- `.env` 中 `MILVUS_DEFAULT_DB=AI_EAM`、`MILVUS_DEFAULT_COLLECTION=ai_eam` 已正确

**前台上传取消按钮：**
- `renderFileUpload()` 新增 `AbortController`，上传期间显示红色"取消上传"按钮
- 点击取消 → `abortController.abort()` → `catch` 中捕获 `AbortError` → 显示"已取消上传"
- 取消后按钮恢复，可重新选择文件上传

### 17.3 修改文件
| 文件 | 变更 |
|------|------|
| `.env` | `KB_BUCKET_NAME` 改为 `xiangmu` |
| `app/config/settings.py` | `KB_BUCKET_NAME` 默认值改为 `xiangmu` |
| `frontend/main.html` | `renderFileUpload` 添加 AbortController 取消功能 |

---

## 18. 第九阶段：报价单图片识别优化与表格展示

### 18.1 问题现象
- 图片上传到 MinIO 后向量化失败，"解析失败: Request timed out"
- Ollama qwen3.5:0.8B 本地模型在 CPU 上处理图片极慢（>4分钟），超时
- 硅基流动多个视觉模型下架或不可用

### 18.2 解决方案

#### AI 视觉模型选型历程
| 模型 | 结果 | 原因 |
|------|------|------|
| Qwen/Qwen2.5-VL-7B-Instruct | ❌ 401 Invalid token | API Key 前缀`ssk-`错误 |
| THUDM/GLM-4.1V-9B-Thinking | ❌ 400 Model disabled | 免费模型被禁用 |
| deepseek-ai/DeepSeek-OCR | ❌ 仅返回 `}` | OCR模型不能输出JSON |
| deepseek-ai/deepseek-vl2 | ❌ 已下架 | 模型下线 |
| Qwen/Qwen3-Omni-30B-A3B-Instruct | ✅ 可用 | 硅基流动官方推荐 |

**最终方案：** `Qwen/Qwen3-Omni-30B-A3B-Instruct`（硅基流动云端GPU处理，3-10秒返回）

#### 图片识别完整链路
```
上传图片 → ① 保存 MinIO(xiangmu桶) → ② 硅基流动视觉识别 → ③ 解析JSON → ④ 前端表格展示
```

#### 后端修改
- `.env`: `SILICON_FLOW_VISION_MODEL="Qwen/Qwen3-Omni-30B-A3B-Instruct"`
- `.env`: 修复 `SILICON_FLOW_API_KEY` 前缀为 `sk-`
- `settings.py`: 同步更新默认视觉模型
- `ai_client.py`:
  - 新增 `chat_with_image()` 方法（仅走硅基流动，删除Ollama兜底）
  - 新增 `_chat_with_image_siliconflow()` 方法处理图片base64编码发送
- `quotation.py`:
  - 新增 `_extract_json()` 工具函数剥离 markdown 代码块包裹（` ```json ... ``` `）
  - `json.loads()` 前先调用 `_extract_json()` 清洗文本

#### 前端修改（main.html）
- `renderFileUpload` 新增 `onResult` 回调支持自定义结果渲染
- 新增 `renderQuotationResult()` 函数：
  - 上传成功后以表格展示所有提取的报价条目（备件名称、规格、单价、数量、总价、币种、交期、付款条件、有效期、含税）
  - 多文件上传 → 显示"来源文件"列，所有条目统一表格
  - 解析失败的文件显示错误详情+原始识别文本折叠
  - 表格下方"添加至比价分析"按钮
- 新增 `window.__quotationItems` 全局变量累加报价条目
- 新增 `addToComparison()` / `loadAccumulatedItems()` / `clearAccumulatedItems()`
- 比价分析页面显示已积累条目数，支持"加载到文本框"/"清空"

### 18.4 报价单上传与比价分析页面合并（2026-06-06）

**用户需求：**
- 删除供应商ID/名称无用字段
- 将比价分析合并到上传页面
- 图片识别后自动生成表格，PDF/Excel/Word同理
- 三个按钮：上传、取消上传、比价分析

**修改内容：**

**报价单上传页面（main.html）：**
- 完全重写，不再使用通用 `renderFileUpload`
- 自定义布局：文件选择区 → 文件信息 → 已识别条数统计 → 备件名称输入 → 三按钮（上传/取消上传/比价分析）
- 上传成功后调用 `renderQuotationResult(..., true)` 自动积累条目
- 比价分析结果在同一页面内联显示（`#qz_compare_result`）

**renderQuotationResult 改造：**
- 新增 `autoAccum` 参数，为 true 时自动将识别条目累积到 `window.__quotationItems`
- 删除旧的"添加至比价分析"按钮，改为"立即比价分析 →"快捷跳转

**新工具函数：**
- `updateAccumDisplay()` - 更新页面上已识别条目数的显示
- `clearQuotationItems()` - 清空累积数据
- `doQuotationCompare()` - 从合并页面发起比价分析API调用，结果内联显示

**比价分析独立页面简化：**
- 保留独立入口但大幅简化，不再有积累加载/清空等复杂逻辑
- 提示用户"也可在上传报价单页面直接操作"

### 18.5 比价分析文本+文件合并（2026-06-06）
- 比价分析页面改为 tab 切换：文本输入 | 上传文件
- 文本输入：保持原有 JSON 编辑 + 备件名称 + 比价按钮
- 上传文件：选择报价文件 → 上传识别 → 自动提交比价分析
- 新增 `switchPriceTab()` / `doPriceCompareFile()`

### 18.6 数据看板自然语言输出（2026-06-06）
- `text2sql_service.py` 不再生成 SQL JSON，改为 AI 直接回答业务问题
- 输出自然语言文本（如"本月采购总额为 ¥128,500"）
- 数据库：`generate_sql()` 改用 `ai_client.chat()` 而非 `chat_with_json()`

### 18.7 去重 AI审批页面（2026-06-06）
- 管理员菜单和数据与决策组中移除重复的"AI审批"入口
- 仅保留"审批决策辅助"入口，leader 和 admin 均可访问
- `allRoles` 中移除 `AI审批`

### 18.8 维修作业录入合并页面（2026-06-06）

**变动内容：**
- 将"语音转文字""图片分析""生成报告"三个独立页面合并为一个"维修作业录入"页面
- 四个 tab：🎤 语音识别 | 📸 图片分析 | 📝 生成报告 | 💾 录入知识库
- 旧页面 ID 保留为别名（指向 `renderRepairWork`）
- 菜单替换为单个"维修作业录入"

**新增功能（录入知识库 tab）：**
- 设备ID + 故障描述 + 维修方案 → 录入到 Milvus 知识库
- 支持附件上传至 MinIO（维修附件桶）
- 之后知识库搜索和 AI 故障诊断可检索到

**前后端新增：**
- `renderRepairWork()` / `switchRWTab()` / `toggleRWRecord()` / `doRWVoiceTrans()` / `doRWImageAnalysis()` / `doRWStore()` 
- 后端 `knowledge.py` 新增 POST `/ingest` 和 POST `/upload-attachment` 端点

### 18.9 向量模型配置
| 环节 | 模型 | 位置 |
|------|------|------|
| 图片文字提取 | 硅基流动 Qwen3-Omni-30B-A3B-Instruct | `.env` → `SILICON_FLOW_VISION_MODEL` |
| 文本向量化 | Ollama nomic-embed-text:latest | `.env` → `EMBEDDING_MODEL` |
| 向量存储 | Milvus AI_EAM 库 | `.env` → `MILVUS_DEFAULT_DB` |

---

## 19. 第七阶段：全栈中文化与合同存储对齐（2026-06-06）

> 本节为 Cursor 会话当日补充记录（此前 18.x 已写完，但本节内容当时未入库）。

### 19.1 数据库与模型中文化
- **25 张业务表**改为中文表名 + 中文列名；`id` / `created_at` / `updated_at` 保持英文
- 新增 `app/rebuild_cn_tables.py`：删英文旧表 → 删旧中文表 → `create_all` 重建
- 全部 `app/models/*.py` 同步：`__tablename__`、 `Column("中文列名")`、`ForeignKey("中文表.id")`
- Windows MySQL 下 `BOM清单` 实际存储为 `bom清单`，模型 `__tablename__` 已对齐
- `app/init_data.py`：构造参数改中文属性名；密码改用 `hash_password`；审批/申购等 magic user ID 改为按角色查 ID

### 19.2 API 层与 Schema 中文化
- `app/schemas/user.py`、`app/core/security.py`（JWT：`用户ID`/`用户名`/`角色`，兼容旧英文 key）
- 各角色 API 请求/响应 DTO 改为中文字段（auth、dispatch、dashboard、diagnosis、work_order、knowledge、exam、requisition、sharing、equipment、lcc、quotation、contract、supplier、approval 等）
- `knowledge.py` 上传响应改为 `入库切片数`/`来源`/`存储信息`；`work_order` 语音返回 `文本`
- 上传临时目录增加 `try/finally` + `shutil.rmtree`（`knowledge.py`、`work_order.py`）
- `IngestTextRequest.元数据` 改为 `Field(default_factory=dict)` 避免可变默认值

### 19.3 前端与测试脚本对齐
- `frontend/main.html`、`frontend/login.html`：登录体、localStorage 用户对象、各业务 API 请求/响应字段改中文
- 修复 `main.html` 第 924 行 `??` 与 `||` 混用导致整页脚本无法执行、一直显示「加载中」的语法错误
- `bootstrap()` 增加 10s 超时；兼容旧 token 中 `role`/`username` 等英文字段
- `test_api.py`、`smoke_test.py`：中文字段 + 测试账号对齐 `init_data`（`supervisor1`/`engineer1` 等，默认密码 `123456`/`admin123`）
- `scripts/seed_quotation_data.py`、`sql/init.sql` 改为中文表/列名

### 19.4 合同查询：数据库与 MinIO 精准匹配
**问题：** `合同` 表有 3 条灌数记录，但「合同查询」页面为空——原接口只列 MinIO，且 `init_data` 未实际上传文件。

**方案：**
- 新增 `app/services/contract_storage.py`：解析 `minio://contracts/CT001.pdf` → 对象名 `contracts/CT001.pdf`
- `minio_client.put_object_exact()`：按指定对象名上传（非 UUID）
- `GET /purchaser/contract/list` 重写：查 `合同` 表 + JOIN `供应商`，再与 MinIO `contracts/` 前缀文件按对象名匹配；返回 `列表`/`已匹配数`/`未匹配数`/`MinIO孤立文件`
- `init_data.init_contracts()` 灌数后自动 `sync_contracts_to_minio()`
- 新增 `app/sync_contract_minio.py`：已有库数据单独同步 MinIO
- 上传审查文件改为 `contracts/{原文件名}`，便于与库记录对齐
- `requirements.txt` 补充 `minio`、`argon2-cffi`、`pycryptodome`

**前端：**
- 「合同查询」展示合同编号、供应商、签订日期、匹配状态、下载
- `normalizeContractList()` 兼容旧接口返回的 `文件列表`（后端未重启时 admin 也能看到数据）

**权限说明：** admin 在 `allow_purchaser` 白名单内，可正常访问合同接口；此前看不到合同是前后端字段名不一致，非权限问题。

### 19.5 规范文档
- `.cursor/rules/eam-backend.mdc` 更新：Python 中文属性 + 中文 DB 表/列名；要求每次改动写入 `project_history.md`

### 19.6 遗留与运行注意
- AI Service 层内部部分响应仍为英文（如考核 `scenario`、合同审查 `risk_level`），由 API/前端做兼容读取
- 改 API 或模型后需**重启 FastAPI**，否则旧进程仍用旧 schema
- MinIO 同步：`python -m app.sync_contract_minio`（conda 环境需安装 `argon2-cffi`、`pycryptodome`）
- `text2sql_service` 仍为 AI 直接回答，不执行真实 SQL；自然语言问「签订几次合同」不能替代数据库统计

---

## 20. 维修手册上传字段对齐与多文件向量化（2026-06-07）

**问题：** 上传维修手册返回 `Field required: body.file`。前端 `renderFileUpload` 统一用 multipart 字段名 `files`，后端 `upload-manual` 原参数为 `file`，字段名不一致导致校验失败。

**修复：**
- `knowledge.py` `upload_manual` 改为 `files: list[UploadFile]` + 可选 `source: Form`，逐文件 MinIO 存储并调用 `rag_service.ingest_manual` 切片向量化入 Milvus
- 响应结构：`total_files` + `files[]`（含 `ingested_chunks`、`source`、`filename`、`storage`）
- `frontend/main.html`「上传维修手册」启用 `multiple: true`，支持批量选择

**调用说明：** Swagger/Postman 须使用 `multipart/form-data`，文件字段名为 **`files`**（可重复），可选 `source` 作为向量库来源前缀。

### 20.1 多格式文本提取（DOC/PNG 等）
- `rag_service._extract_text` 按扩展名路由：PDF（pdfplumber）、DOCX（python-docx）、DOC（Windows Word COM / antiword）、PNG/JPG（**硅基流动视觉模型 OCR**）、纯文本（utf-8/gbk 自动探测）
- `ai_client.extract_document_text_from_image()` 统一封装图片 OCR，需配置 `.env` → `SILICON_FLOW_API_KEY` / `SILICON_FLOW_VISION_MODEL`
- 提取结果为空时抛出明确错误，避免空向量入库
- 多文件上传单文件失败不影响其他文件（返回 `error` 字段）
- `requirements.txt` 新增 `python-docx==1.1.2`

### 20.4 `.doc` 解析增强
- `_extract_doc` 四级回退：Word COM（`DispatchEx`）→ LibreOffice 转 txt → `olefile` 提取 WordDocument 流 → antiword
- 新增依赖 `olefile==0.47`；仍失败时提示安装 Word/LibreOffice 或另存 docx

### 20.5 `.docx` 误标后缀自动识别
- 按文件头（`PK` / OLE）识别真实格式，`.doc` 改后缀为 `.docx` 时自动走 doc 解析链
- `Package not found` 不再直接失败，会回退 olefile/Word/LibreOffice 解析

### 20.6 Ollama embedding 500 错误说明
- 实测 `GET /api/tags` 正常但 `POST /api/embed` 返回 500：`llama-server binary not found`（Ollama 0.30.x 安装不完整）
- 已向量化迁移至硅基流动，不再依赖 Ollama embedding

### 20.7 向量化切换硅基流动 Qwen3-VL-Embedding-8B
- 删除 `OllamaEmbedder`，新增 `SiliconFlowEmbedder`（OpenAI `/v1/embeddings` 兼容接口）
- 默认模型 `Qwen/Qwen3-VL-Embedding-8B`，向量维度 `EMBEDDING_DIM=4096`
- Milvus 集合维度校验：旧 768 维集合需删除后重建再入库
- `.env` / `settings.py`：`EMBEDDING_STRATEGY=siliconflow`，`SILICON_FLOW_EMBEDDING_MODEL` 更新

### 20.8 Milvus 使用 AI_EAM 库而非 default
- 根因：`milvus_client.connect()` 未传 `db_name`，pymilvus 默认连 `default` 库，忽略 `.env` 的 `MILVUS_DEFAULT_DB=AI_EAM`
- 修复：`connections.connect(..., db_name=settings.MILVUS_DEFAULT_DB)`，Collection/utility 统一 `using=MILVUS_DEFAULT_ALIAS`
- `.env` 区分：`MILVUS_DEFAULT_ALIAS=default`（连接别名）、`MILVUS_DEFAULT_DB=AI_EAM`（数据库名）

### 20.9 扫描版 PDF OCR 回退
- 向量化模型只处理**文本**，不负责读 PDF；原 `pdfplumber` 对扫描版 PDF 提取为空导致入库失败
- PDF 解析链：pdfplumber → PyMuPDF 文本层 → 仍为空则 pymupdf 逐页转 PNG + 硅基流动视觉 OCR（最多 30 页）
- 新增依赖 `pymupdf==1.24.14`

### 20.10 知识库搜索字段与结果展示
- `KnowledgeQuery` 改为中文字段 `问题` / `返回条数`（兼容 `question` / `top_k`）
- 搜索响应返回 `回答` + `引用片段[]`（含来源、完整内容、距离）
- 前端 `doKBSearch` 展示 AI 综合回答与各片段全文，不再只显示 JSON 校验错误

### 20.11 管理员账号脚本
- 新增 `app/create_admin.py`：`python -m app.create_admin` 创建或重置 admin（默认密码 admin123）

### 20.2 图片 OCR 统一硅基流动
- 移除 `rag_service` 中 PaddleOCR 路径，图片类文件仅走 `ai_client.extract_document_text_from_image()`
- `chat_with_image()` 增加 API Key 校验与 `mime_type` 参数（PNG 等不再误标为 jpeg）

### 20.3 上传字段名统一为 `files`（修复 422 Field required: file）
**根因：** 前端 `renderFileUpload` 固定用 multipart 字段名 `files`，但部分后端仍为 `file: UploadFile`；且 uvicorn 未热重载时 OpenAPI/进程仍跑旧代码。

**修复：**
- `knowledge.py`：`upload-manual`、`upload-attachment` 均改为 `files: list[UploadFile]`（附件取首个）
- `contract.py` `review-file` 改为 `files: list[UploadFile]`（取首个审查）
- `main.html` 维修附件 FormData 字段 `file` → `files`
- 已重启后端并验证：OpenAPI 四项上传接口均为 `files`；`files` 上传 HTTP 200；错误字段 `file` 返回 422

*文档结束 | 最后更新：2026-06-07*