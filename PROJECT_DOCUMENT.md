# AI-EAM 智能设备全生命周期管理系统 项目书

**版本**: v1.0.0
**编写日期**: 2026-06-18
**项目路径**: `d:\EAM-AI`

---

## 1. 项目背景与目标

### 1.1 项目背景

工业制造企业在设备管理过程中普遍存在以下痛点：

- **设备台账分散**：设备信息、维修记录、巡检记录散落在不同表格中，难以统一管理。
- **故障诊断依赖经验**：工程师个人能力差异大，新手上手慢，缺少历史案例的智能推荐。
- **备件采购效率低**：采购决策缺乏数据支撑，供应商风险难以及时识别。
- **维修知识沉淀难**：维修手册、故障案例、技术文档利用率低，难以快速检索和复用。
- **多模态数据未打通**：设备故障图片、PDF 手册、语音记录等数据未被有效利用。

### 1.2 项目目标

构建一套 **AI 驱动的智能设备全生命周期管理系统（AI-EAM）**，实现：

1. **设备台账统一管理**：覆盖设备、BOM、工单、巡检、维护计划等核心资产数据。
2. **AI 辅助故障诊断**：基于历史故障案例和维修手册，提供智能诊断建议。
3. **知识库智能检索**：支持文本、PDF、图片、语音等多模态知识的统一检索。
4. **预测性维护**：结合 IoT 传感器数据预测设备失效风险。
5. **采购与供应商管理**：AI 辅助比价、合同审查、供应商风险评估。
6. **领导决策支持**：通过数据看板、LCC 分析、审批决策辅助提升管理效率。
7. **工程师技能考核**：基于虚拟故障场景的 AI 考核系统。

---

## 2. 系统架构

### 2.1 总体架构

```text
┌─────────────────────────────────────────────────────────────────────┐
│                          前端层 (Frontend)                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │ main.html    │  │ login.html   │  │ 静态资源     │               │
│  │ (单页应用)   │  │ (登录页)     │  │              │               │
│  └──────────────┘  └──────────────┘  └──────────────┘               │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ HTTP/REST
┌──────────────────────────────▼──────────────────────────────────────┐
│                         API 网关层 (FastAPI)                         │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  CORS / 请求日志 / 全局异常处理 / JWT 鉴权                       │  │
│  └───────────────────────────────────────────────────────────────┘  │
│  ┌────────────┬────────────┬────────────┬────────────┬───────────┐  │
│  │ 公共模块   │ 工程师模块 │ 主管模块   │ 采购员模块 │ 领导模块  │  │
│  └────────────┴────────────┴────────────┴────────────┴───────────┘  │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│                         服务层 (Services)                            │
│  AI Services: RAG / 故障诊断 / 预测性维护 / 多模态 / 考核 / 采购      │
│  Agent Services: BOM检查 / 申购分析 / 调拨评估 / 供应商风险 / 比价   │
│  Approval / LCC / Text2SQL / Contract / Sourcing                     │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│                         基础设施层                                   │
│  MySQL(业务数据)  Milvus(向量检索)  MinIO(对象存储)  Redis(缓存)      │
│  Neo4j(可选图数据库)  硅基流动/DeepSeek(LLM & Embedding API)          │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 技术栈

| 层级 | 技术选型 | 说明 |
|------|---------|------|
| 后端框架 | FastAPI 0.115.0 | 异步高性能 Python Web 框架 |
| ASGI 服务器 | Uvicorn 0.30.0 | 运行 FastAPI 应用 |
| 数据库 ORM | SQLAlchemy 2.0.35 + aiomysql 0.2.0 | 异步 MySQL 访问 |
| 向量数据库 | Milvus 2.4.0 | 存储文本/图像向量，支持 COSINE 相似度 |
| 对象存储 | Minio 7.2.20 | 存储文件、图片、音频、合同附件 |
| 缓存 | Redis | 会话缓存、速率限制等 |
| 大模型 API | 硅基流动 (SiliconFlow) | DeepSeek-R1、Qwen3-VL-Embedding-8B、Qwen3-Omni |
| 备用大模型 | DeepSeek API | deepseek-v4-flash |
| 文档解析 | PyMuPDF / pdfplumber / python-docx / paddleocr | PDF、Word、OCR |
| 语音识别 | openai-whisper | 维修语音转文字 |
| 前端 | 原生 HTML + CSS + JavaScript | 单页应用，无需构建 |
| 部署 | Docker Compose | MySQL + etcd + MinIO + Milvus + Attu |

---

## 3. 功能模块

### 3.1 角色与权限

系统支持五种角色，基于 JWT Token 鉴权：

| 角色 | 标识 | 核心权限 |
|------|------|---------|
| 管理员 | `admin` | 用户管理、所有模块访问 |
| 工程师 | `engineer` | 故障诊断、知识库、维修作业、技能考核、IoT 分析 |
| 主管 | `supervisor` | BOM 检查、申购分析、调拨评估、工程师调派 |
| 采购员 | `purchaser` | 比价分析、合同审查/查询、供应商风险评估/推荐、价格趋势 |
| 领导 | `leader` | 审批决策辅助、数据看板、数据洞察、LCC 分析 |

### 3.2 模块清单

#### 3.2.1 公共模块 (`/api/v1/common`)

| 接口 | 功能 |
|------|------|
| `POST /auth/login` | 用户登录，返回 JWT |
| `POST /auth/register` | 用户注册 |
| `GET  /auth/users` | 用户列表（管理员） |
| `POST /auth/change-role` | 修改用户角色 |
| `POST /upload/file` | 通用文件上传 |

#### 3.2.2 工程师模块 (`/api/v1/engineer`)

| 模块 | 接口示例 | 功能描述 |
|------|---------|---------|
| AI 故障诊断 | `POST /diagnose` | 输入故障描述，AI 分析可能原因与解决方案 |
| 知识库搜索 | `POST /knowledge/search` | 向量检索维修手册知识片段 |
| 上传维修手册 | `POST /knowledge/upload-manual` | 上传 PDF/Word/TXT/图片，自动切片并向量化 |
| 故障案例 | `POST /knowledge/fault-cases/search` | 检索历史相似故障案例 |
| 录入故障案例 | `POST /knowledge/ingest-case` | 手动录入故障案例到向量库 |
| 录入维修数据 | `POST /knowledge/ingest` | 维修文本向量化入库 |
| 多模态知识库 | `POST /knowledge/multimodal-search` | 图文混合检索，返回文本+图片 |
| 统一上传 | `POST /knowledge/upload` | LLM 自动判断简单文本 or 多模态版面分析 |
| 维修作业录入 | `POST /work-order/speech-to-text` | 语音转文字 |
| | `POST /work-order/analyze-image` | 故障图片分析 |
| | `POST /work-order/generate-report` | 生成结构化维修报告 |
| 技能考核 | `POST /exam/start` | 启动虚拟故障考核 |
| | `POST /exam/answer` | 提交答案并评估 |
| | `POST /exam/submit` | 批量提交并评分 |
| | `POST /exam/skill-radar` | 生成技能雷达图 |
| 预测性维护 | `POST /predictive/analyze` | 分析 IoT 传感器数据，预测失效风险 |

#### 3.2.3 主管模块 (`/api/v1/supervisor`)

| 模块 | 接口示例 | 功能描述 |
|------|---------|---------|
| BOM 检查 | `POST /equipment/check-bom` | 检查 BOM 清单与维修记录一致性 |
| 申购分析 | `POST /requisition/analyze` | AI 分析备件申购合理性 |
| 调拨评估 | `POST /transfer/analyze` | 评估备件调拨建议 |
| 工程师调派 | `POST /dispatch/create` | 创建调派记录 |
| | `POST /dispatch/recommend` | 基于技能和距离推荐工程师 |

#### 3.2.4 采购员模块 (`/api/v1/purchaser`)

| 模块 | 接口示例 | 功能描述 |
|------|---------|---------|
| 比价分析 | `POST /quotation/compare` | 多供应商报价自动比对 |
| 合同审查 | `POST /contract/review` | AI 审查合同风险条款 |
| 合同文件审查 | `POST /contract/review-file` | 上传合同文件并审查 |
| 合同列表 | `GET /contract/list` | 查询合同记录 |
| 供应商风险评估 | `POST /supplier/risk-check` | 监控并评估供应商风险 |
| 供应商推荐 | `POST /supplier/sourcing` | 根据备件规格推荐供应商 |
| 价格趋势 | `POST /supplier/price-trend` | 分析大宗商品价格趋势 |

#### 3.2.5 领导模块 (`/api/v1/leader`)

| 模块 | 接口示例 | 功能描述 |
|------|---------|---------|
| 审批决策辅助 | `POST /approval/review` | AI 生成审批建议和风险提示 |
| 数据看板 | `GET /dashboard/metrics` | 关键业务指标 |
| 数据洞察 | `POST /dashboard/text2sql` | 自然语言转 SQL 查询 |
| LCC 分析 | `POST /lcc/analyze` | 设备全生命周期成本分析 |

---

## 4. 数据库设计

### 4.1 MySQL 业务表

系统使用中文表名和字段名，主要表包括：

| 表名 | 说明 |
|------|------|
| `用户` | 用户账号、密码哈希、角色、真实姓名等 |
| `技能记录` | 工程师各技能维度评分 |
| `考核记录` | AI 考核记录与得分 |
| `设备` | 设备台账基础信息 |
| `bom清单` | 设备 BOM 备件清单 |
| `工单` | 维修工单记录 |
| `巡检记录` | 设备巡检数据 |
| `维护计划` | AI 预测生成的维护计划 |
| `备件` / `仓库` / `库存记录` | 备件库存管理 |
| `申购单` / `调拨单` / `呆滞预警` | 备件流转与预警 |
| `供应商` / `供应商品类` / `报价单` / `比价记录` / `合同` | 采购与供应商管理 |
| `供应商风险预警` / `大宗商品价格` / `寻源推荐` | 供应商风险与寻源 |
| `审批记录` / `成本分析` | 审批流程与 LCC 分析 |
| `工程师调派` | 工程师派工记录 |

### 4.2 Milvus 向量集合

| 集合名 | 用途 | 距离度量 |
|--------|------|---------|
| `equipment_knowledge` | 维修手册文本切片向量 | COSINE |
| `fault_cases` | 故障案例向量 | COSINE |
| `multimodal_knowledge` | 图文混合 Chunk 向量 | COSINE |

`multimodal_knowledge` 扩展字段：
- `chunk_type`: text / image_with_text / table
- `page_num`: 页码
- `bbox`: 坐标 JSON
- `image_path`: MinIO 图片路径
- `image_hash`: 图片去重哈希

### 4.3 MinIO Bucket

| Bucket | 用途 |
|--------|------|
| `knowledge-base` | 维修手册、故障图片、语音文件、合同附件 |
| `vanna-training-data` | 训练数据（预留） |

---

## 5. 核心 AI 能力

### 5.1 故障诊断

- 接收故障描述 + 设备型号
- 从 `fault_cases` 向量库检索相似案例
- 构造 Prompt 调用 LLM，输出 JSON 格式诊断结果

### 5.2 RAG 知识库

- 文本切片：`RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)`
- Embedding：硅基流动 `Qwen/Qwen3-VL-Embedding-8B`（4096 维）
- 向量存储：Milvus `equipment_knowledge`
- 检索：余弦相似度 Top-K

### 5.3 多模态知识库

- PDF 版面分析：PyMuPDF 提取文本块、图片、坐标、阅读顺序
- 图文混合切片：
  - 将图片与前后标题、正文段落绑定
  - 调用 Vision 模型生成图片描述/OCR 文本
  - 拼接成 `[图标题] + [图描述] + [正文]` 的完整 Chunk
- 元数据保留：图片 MinIO 路径、页码、坐标 bbox
- 检索时同时召回文本切片和原始图片，送入 LLM 生成图文并茂的回答

### 5.4 统一上传与策略决策

`POST /knowledge/upload` 接收任意文件后，由 LLM 根据文件类型和内容自动决策：

- `simple_text`: 纯文本/Word/普通 PDF → 文本切片 + 向量入库
- `multimodal_layout`: 含图/表/扫描版的 PDF → 版面分析 + 图文混合切片

### 5.5 维修报告生成

- 语音文件 → Whisper 转文字
- 故障图片 → Vision 模型分析 JSON
- 综合语音、图片、设备信息 → LLM 生成结构化维修报告

### 5.6 预测性维护

- 接收 IoT 传感器数据 JSON
- LLM 分析健康状态、预测失效部件、推荐备件与操作时间

### 5.7 采购与供应商

- **比价分析**：解析多供应商报价单，生成比价表与推荐
- **合同审查**：识别风险条款、给出修改建议
- **供应商风险评估**：监控供应商风险并生成评估报告
- **价格趋势**：分析大宗商品价格，预测未来走势

---

## 6. 接口设计

### 6.1 统一响应格式

```json
{
  "code": 200,
  "msg": "success",
  "data": {}
}
```

### 6.2 认证方式

- 登录接口返回 `access_token`
- 后续请求在 Header 中携带：`Authorization: Bearer <token>`

### 6.3 主要接口示例

#### 登录
```http
POST /api/v1/common/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

#### 上传维修手册
```http
POST /api/v1/engineer/knowledge/upload-manual
Authorization: Bearer <token>
Content-Type: multipart/form-data

files: <PDF/Word/TXT/图片>
source: 设备维修手册
```

#### 知识库搜索
```http
POST /api/v1/engineer/knowledge/search
Authorization: Bearer <token>
Content-Type: application/json

{
  "question": "数控车床主轴异响如何处理？",
  "top_k": 5
}
```

#### 多模态知识库搜索
```http
POST /api/v1/engineer/knowledge/multimodal-search
Authorization: Bearer <token>
Content-Type: application/json

{
  "question": "液压系统压力不足的原因",
  "top_k": 5,
  "return_images": true
}
```

---

## 7. 前端设计

### 7.1 技术方案

- 单页应用（SPA），纯原生 HTML/CSS/JavaScript
- 无需构建工具，直接由 FastAPI 挂载为静态文件
- 响应式布局，适配桌面端

### 7.2 页面结构

- `login.html`：登录页
- `main.html`：主应用，包含：
  - 侧边栏导航（按角色动态渲染）
  - 主内容区（根据路由渲染不同页面）
  - 统一 Toast 提示、文件上传组件

### 7.3 角色导航

以工程师角色为例：

```text
故障诊断
  ├─ AI 故障诊断
  ├─ 知识库搜索
  ├─ 故障案例
  └─ 多模态知识库 ⭐ 新增
维修作业
  ├─ 上传维修手册
  └─ 维修作业录入
技能与监控
  ├─ 技能考核
  └─ IoT 分析
文件
  └─ 文件上传
```

### 7.4 新增多模态知识库页面

- **上传区**：拖拽上传 PDF/图片，支持取消上传
- **进度展示**：策略类型、Chunk 统计、耗时
- **检索区**：输入问题，返回 AI 综合回答
- **图片画廊**：展示检索到的相关图片
- **相关片段**：文本 Chunk 列表，含类型标签、页码、相似度距离

---

## 8. 部署说明

### 8.1 环境依赖

- Python 3.11+
- Docker & Docker Compose
- 硅基流动 API Key（或 DeepSeek API Key）

### 8.2 安装依赖

```bash
pip install -r requirements.txt
```

### 8.3 启动基础设施

```bash
docker-compose up -d
```

将启动：
- MySQL: `127.0.0.1:3306`
- MinIO: `127.0.0.1:9100`
- Milvus: `127.0.0.1:19530`
- Attu (Milvus UI): `127.0.0.1:8000`

### 8.4 配置环境变量

创建 `.env` 文件：

```env
SILICON_FLOW_API_KEY=your_api_key
MYSQL_PASSWORD=root123456
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
JWT_SECRET_KEY=your_jwt_secret
```

### 8.5 启动后端服务

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

访问：`http://127.0.0.1:8000`

### 8.6 初始化数据

首次启动时，`main.py` 的 `lifespan` 会自动创建表结构。
`app/init_data.py` 会在表为空时插入默认用户和演示数据。

默认账号：

| 用户名 | 密码 | 角色 |
|--------|------|------|
| `admin` | `admin123` | 管理员 |
| `engineer1` | `123456` | 工程师 |
| `supervisor1` | `123456` | 主管 |
| `purchaser1` | `123456` | 采购员 |
| `leader1` | `123456` | 领导 |

---

## 9. 待办事项

| 优先级 | 事项 | 说明 |
|--------|------|------|
| 高 | 多模态知识库前端联调 | 确保上传、检索接口与后端完全打通 |
| 高 | 前端字段名统一 | 已修复登录、用户列表字段名，需全面检查其他页面 |
| 中 | 端口冲突处理 | docker-compose 中 Attu 占用 8000，与后端冲突 |
| 中 | 多模态 Chunk 图片去重 | `image_hash` 已实现，需验证去重效果 |
| 中 | 向量集合重建 | 距离度量改为 COSINE 后，旧集合需删除重建 |
| 中 | 用户列表加载优化 | 支持分页、搜索、批量操作 |
| 低 | 前端构建迁移 | 长期可考虑 Vue/React 重构 |
| 低 | 单元测试与接口文档 | 补充 pytest 和 Swagger 描述 |

---

## 10. 项目文件结构

```
d:\EAM-AI
├── app
│   ├── api/v1              # API 路由（按角色分模块）
│   ├── config              # 配置文件
│   ├── core                # 数据库、安全、异常、依赖
│   ├── middleware          # 中间件
│   ├── models              # SQLAlchemy 模型
│   ├── schemas             # Pydantic 模型
│   ├── services/ai_services # AI 业务服务
│   ├── utils               # 工具类（Milvus、MinIO、AI Client、PDF 解析等）
│   ├── main.py             # FastAPI 应用入口
│   └── init_data.py        # 演示数据初始化
├── frontend
│   ├── main.html           # 主应用
│   └── login.html          # 登录页
├── scripts                 # 初始化与数据脚本
├── docker-compose.yml      # 基础设施编排
├── requirements.txt        # Python 依赖
└── PROJECT_DOCUMENT.md     # 本项目书
```

---

## 11. 总结

AI-EAM 项目致力于打造一套面向工业设备管理的智能化平台，覆盖设备台账、故障诊断、维修作业、知识管理、采购供应、领导决策等全链路场景。通过大模型、向量检索、多模态理解等技术，有效提升设备管理效率、降低故障停机损失、沉淀企业维修知识资产。

当前项目已具备完整的基础架构和核心功能，多模态知识库作为最新增强能力，已实现 PDF 版面分析、图文混合切片、统一上传策略决策、图文混合检索等关键能力，后续重点是前后端联调与生产化打磨。
