-- ============================================
-- AI-EAM 数据库初始化脚本
-- 数据库: eam_ai
-- 账户: root / 123456
-- ============================================

CREATE DATABASE IF NOT EXISTS eam_ai DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE eam_ai;

-- 1. 用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID',
    username VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    real_name VARCHAR(50) COMMENT '真实姓名',
    email VARCHAR(100) COMMENT '邮箱',
    phone VARCHAR(20) COMMENT '手机号',
    role VARCHAR(20) DEFAULT 'engineer' COMMENT '角色: engineer/supervisor/purchaser/leader/admin',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否激活',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_role (role),
    INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 2. 技能记录表
CREATE TABLE IF NOT EXISTS skill_records (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '记录ID',
    user_id INT NOT NULL COMMENT '用户ID',
    skill_dimension VARCHAR(50) NOT NULL COMMENT '技能维度: 电气/机械/液压/PLC/安全规范',
    score INT DEFAULT 0 COMMENT '技能评分(0-100)',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_user_id (user_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='技能记录表';

-- 3. 考核记录表
CREATE TABLE IF NOT EXISTS exam_records (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '记录ID',
    user_id INT NOT NULL COMMENT '用户ID',
    exam_type VARCHAR(50) COMMENT '考核类型: virtual_fault/dialogue',
    scenario VARCHAR(500) COMMENT '考核场景描述',
    total_score INT COMMENT '总得分',
    detail VARCHAR(2000) COMMENT '考核详情JSON',
    status VARCHAR(20) DEFAULT 'in_progress' COMMENT '状态: in_progress/completed',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_user_id (user_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='考核记录表';

-- 4. 设备表
CREATE TABLE IF NOT EXISTS equipments (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '设备ID',
    code VARCHAR(50) UNIQUE NOT NULL COMMENT '设备编码',
    name VARCHAR(200) NOT NULL COMMENT '设备名称',
    model VARCHAR(100) COMMENT '设备型号',
    category VARCHAR(100) COMMENT '设备分类',
    factory_code VARCHAR(50) COMMENT '所属厂区',
    workshop VARCHAR(100) COMMENT '所属车间',
    line VARCHAR(100) COMMENT '所属产线',
    status VARCHAR(20) DEFAULT 'running' COMMENT '状态: running/stopped/maintenance/scrapped',
    purchase_date VARCHAR(20) COMMENT '采购日期',
    warranty_expiry VARCHAR(20) COMMENT '质保到期日',
    manufacturer VARCHAR(200) COMMENT '制造商',
    supplier_id INT COMMENT '供应商ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_code (code),
    INDEX idx_status (status),
    INDEX idx_factory (factory_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='设备表';

-- 5. BOM表
CREATE TABLE IF NOT EXISTS bom_items (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'BOM项ID',
    equipment_id INT NOT NULL COMMENT '设备ID',
    spare_part_id INT NOT NULL COMMENT '备件ID',
    quantity INT DEFAULT 1 COMMENT '标准用量',
    is_critical INT DEFAULT 0 COMMENT '是否关键备件',
    position VARCHAR(100) COMMENT '安装位置',
    ai_confidence FLOAT COMMENT 'AI置信度(0-1)',
    ai_evidence JSON COMMENT 'AI证据来源',
    is_suspected_outdated INT DEFAULT 0 COMMENT '是否疑似过时',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_equipment (equipment_id),
    INDEX idx_spare_part (spare_part_id),
    FOREIGN KEY (equipment_id) REFERENCES equipments(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='BOM表';

-- 6. 工单表
CREATE TABLE IF NOT EXISTS work_orders (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '工单ID',
    order_no VARCHAR(50) UNIQUE NOT NULL COMMENT '工单号',
    equipment_id INT NOT NULL COMMENT '设备ID',
    fault_phenomenon TEXT COMMENT '故障现象',
    fault_cause TEXT COMMENT '故障原因(AI诊断)',
    fault_cause_confidence FLOAT COMMENT 'AI诊断置信度',
    action_taken TEXT COMMENT '处理措施',
    parts_replaced JSON COMMENT '更换备件列表',
    time_spent INT COMMENT '耗时(分钟)',
    voice_text TEXT COMMENT '语音转译文本',
    photo_urls JSON COMMENT '故障照片URL列表',
    report_content TEXT COMMENT 'AI生成的维修报告',
    status VARCHAR(20) DEFAULT 'pending' COMMENT '状态: pending/in_progress/completed',
    repairer_id INT COMMENT '维修人员ID',
    created_by INT COMMENT '创建人ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_order_no (order_no),
    INDEX idx_equipment (equipment_id),
    INDEX idx_status (status),
    FOREIGN KEY (equipment_id) REFERENCES equipments(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='工单表';

-- 7. 巡检记录表
CREATE TABLE IF NOT EXISTS inspection_records (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '记录ID',
    equipment_id INT NOT NULL COMMENT '设备ID',
    inspector_id INT COMMENT '巡检人员ID',
    inspection_route VARCHAR(100) COMMENT '巡检路线',
    nfc_tag VARCHAR(100) COMMENT 'NFC标签',
    is_normal INT DEFAULT 1 COMMENT '是否正常',
    abnormal_desc TEXT COMMENT '异常描述',
    abnormal_photo_url VARCHAR(500) COMMENT '异常照片',
    linked_work_order_id INT COMMENT '关联工单ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_equipment (equipment_id),
    FOREIGN KEY (equipment_id) REFERENCES equipments(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='巡检记录表';

-- 8. 保养计划表
CREATE TABLE IF NOT EXISTS maintenance_plans (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '计划ID',
    equipment_id INT NOT NULL COMMENT '设备ID',
    plan_type VARCHAR(50) COMMENT '计划类型: preventive/predictive',
    predicted_failure_time VARCHAR(50) COMMENT '预测失效时间',
    ai_prediction TEXT COMMENT 'AI预测描述',
    ai_recommendation TEXT COMMENT 'AI建议措施',
    recommended_part VARCHAR(200) COMMENT '建议更换备件',
    status VARCHAR(20) DEFAULT 'pending' COMMENT '状态',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_equipment (equipment_id),
    FOREIGN KEY (equipment_id) REFERENCES equipments(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='保养计划表';

-- 9. 备件表
CREATE TABLE IF NOT EXISTS spare_parts (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '备件ID',
    sku_code VARCHAR(50) UNIQUE NOT NULL COMMENT 'SKU编码',
    name VARCHAR(200) NOT NULL COMMENT '备件名称',
    specification VARCHAR(500) COMMENT '规格型号',
    category VARCHAR(100) COMMENT '分类',
    unit VARCHAR(20) DEFAULT '个' COMMENT '单位',
    unit_price FLOAT COMMENT '参考单价',
    shelf_life_days INT COMMENT '保质期(天)',
    min_stock INT DEFAULT 0 COMMENT '最小库存',
    max_stock INT DEFAULT 0 COMMENT '最大库存',
    safety_stock INT DEFAULT 0 COMMENT '安全库存',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_sku (sku_code),
    INDEX idx_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='备件表';

-- 10. 仓库表
CREATE TABLE IF NOT EXISTS warehouses (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '仓库ID',
    code VARCHAR(50) UNIQUE NOT NULL COMMENT '仓库编码',
    name VARCHAR(200) NOT NULL COMMENT '仓库名称',
    factory_code VARCHAR(50) COMMENT '所属厂区',
    address VARCHAR(500) COMMENT '地址',
    manager_id INT COMMENT '负责人ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_code (code),
    INDEX idx_factory (factory_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='仓库表';

-- 11. 库存记录表
CREATE TABLE IF NOT EXISTS inventory_records (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '记录ID',
    spare_part_id INT NOT NULL COMMENT '备件ID',
    warehouse_id INT NOT NULL COMMENT '仓库ID',
    location_code VARCHAR(50) COMMENT '库位编码',
    quantity INT DEFAULT 0 COMMENT '账面数量',
    available_quantity INT DEFAULT 0 COMMENT '可用数量',
    reserved_quantity INT DEFAULT 0 COMMENT '预留数量',
    reserved_for VARCHAR(200) COMMENT '预留用途',
    batch_no VARCHAR(50) COMMENT '批次号',
    production_date DATETIME COMMENT '生产日期',
    expiry_date DATETIME COMMENT '过期日期',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_spare_part (spare_part_id),
    INDEX idx_warehouse (warehouse_id),
    FOREIGN KEY (spare_part_id) REFERENCES spare_parts(id) ON DELETE CASCADE,
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='库存记录表';

-- 12. 申购表
CREATE TABLE IF NOT EXISTS requisitions (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '申购ID',
    requisition_no VARCHAR(50) UNIQUE NOT NULL COMMENT '申购单号',
    spare_part_id INT NOT NULL COMMENT '备件ID',
    requester_id INT COMMENT '申请人ID',
    requested_quantity INT NOT NULL COMMENT '申请数量',
    ai_recommended_quantity INT COMMENT 'AI推荐数量',
    ai_recommended_reason TEXT COMMENT 'AI推荐理由',
    ai_review_status VARCHAR(20) COMMENT 'AI审核状态: pass/warning/force_review',
    ai_review_detail JSON COMMENT 'AI审核详情',
    deviation_reason VARCHAR(100) COMMENT '偏离原因',
    deviation_note TEXT COMMENT '偏离补充说明',
    work_order_id INT COMMENT '关联工单ID',
    status VARCHAR(20) DEFAULT 'pending' COMMENT '状态: pending/approved/rejected',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_requisition_no (requisition_no),
    INDEX idx_status (status),
    FOREIGN KEY (spare_part_id) REFERENCES spare_parts(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='申购表';

-- 13. 调拨单表
CREATE TABLE IF NOT EXISTS transfer_orders (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '调拨ID',
    transfer_no VARCHAR(50) UNIQUE NOT NULL COMMENT '调拨单号',
    spare_part_id INT NOT NULL COMMENT '备件ID',
    from_warehouse_id INT NOT NULL COMMENT '调出仓库',
    to_warehouse_id INT NOT NULL COMMENT '调入仓库',
    quantity INT NOT NULL COMMENT '调拨数量',
    ai_feasibility_score FLOAT COMMENT 'AI可行性打分(0-100)',
    ai_analysis JSON COMMENT 'AI分析详情',
    transfer_cost FLOAT COMMENT '调拨总成本',
    waiting_cost FLOAT COMMENT '缺货停工等待成本',
    net_benefit FLOAT COMMENT '净收益',
    recommendation TEXT COMMENT 'AI建议',
    status VARCHAR(20) DEFAULT 'pending' COMMENT '状态: pending/in_transit/completed/cancelled',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_transfer_no (transfer_no),
    INDEX idx_status (status),
    FOREIGN KEY (spare_part_id) REFERENCES spare_parts(id) ON DELETE CASCADE,
    FOREIGN KEY (from_warehouse_id) REFERENCES warehouses(id) ON DELETE CASCADE,
    FOREIGN KEY (to_warehouse_id) REFERENCES warehouses(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='调拨单表';

-- 14. 呆滞预警表
CREATE TABLE IF NOT EXISTS stagnant_alerts (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '预警ID',
    spare_part_id INT NOT NULL COMMENT '备件ID',
    warehouse_id INT NOT NULL COMMENT '仓库ID',
    quantity INT COMMENT '呆滞数量',
    stagnant_days INT COMMENT '呆滞天数',
    ai_prediction_days INT COMMENT 'AI预测即将呆滞天数',
    ai_suggestion TEXT COMMENT 'AI处理建议',
    transfer_suggestion JSON COMMENT '调拨建议',
    status VARCHAR(20) DEFAULT 'active' COMMENT '状态: active/resolved',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_spare_part (spare_part_id),
    INDEX idx_status (status),
    FOREIGN KEY (spare_part_id) REFERENCES spare_parts(id) ON DELETE CASCADE,
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='呆滞预警表';

-- 15. 供应商表
CREATE TABLE IF NOT EXISTS suppliers (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '供应商ID',
    code VARCHAR(50) UNIQUE NOT NULL COMMENT '供应商编码',
    name VARCHAR(200) NOT NULL COMMENT '供应商名称',
    contact_person VARCHAR(100) COMMENT '联系人',
    contact_phone VARCHAR(50) COMMENT '联系电话',
    email VARCHAR(100) COMMENT '邮箱',
    address VARCHAR(500) COMMENT '地址',
    delivery_on_time_rate FLOAT COMMENT '历史交付准时率(%)',
    quality_pass_rate FLOAT COMMENT '质量合格率(%)',
    comprehensive_score FLOAT COMMENT '综合推荐指数(0-100)',
    risk_level VARCHAR(20) DEFAULT 'low' COMMENT '风险等级: low/medium/high/critical',
    risk_tags JSON COMMENT '风险标签列表',
    last_risk_check DATETIME COMMENT '最后风险检查时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_code (code),
    INDEX idx_risk_level (risk_level)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='供应商表';

-- 16. 供应商品类表
CREATE TABLE IF NOT EXISTS supplier_categories (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '品类ID',
    supplier_id INT NOT NULL COMMENT '供应商ID',
    category VARCHAR(100) NOT NULL COMMENT '供应品类',
    is_qualified INT DEFAULT 1 COMMENT '是否合格供应商',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_supplier (supplier_id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='供应商品类表';

-- 17. 报价单表
CREATE TABLE IF NOT EXISTS quotations (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '报价单ID',
    quotation_no VARCHAR(50) UNIQUE NOT NULL COMMENT '报价单号',
    supplier_id INT NOT NULL COMMENT '供应商ID',
    purchase_request_id INT COMMENT '关联采购申请ID',
    items JSON COMMENT '报价明细',
    raw_file_path VARCHAR(500) COMMENT '原始报价单文件路径',
    ocr_status VARCHAR(20) DEFAULT 'pending' COMMENT 'OCR状态: pending/success/failed',
    ocr_confidence FLOAT COMMENT 'OCR置信度',
    status VARCHAR(20) DEFAULT 'received' COMMENT '状态',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_quotation_no (quotation_no),
    INDEX idx_supplier (supplier_id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='报价单表';

-- 18. 比价单表
CREATE TABLE IF NOT EXISTS price_comparisons (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '比价单ID',
    comparison_no VARCHAR(50) UNIQUE NOT NULL COMMENT '比价单号',
    spare_part_id INT COMMENT '备件ID',
    quotation_ids JSON COMMENT '参与比价的报价单ID列表',
    comparison_result JSON COMMENT '比价结果',
    created_by INT COMMENT '创建人ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_comparison_no (comparison_no)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='比价单表';

-- 19. 合同表
CREATE TABLE IF NOT EXISTS contracts (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '合同ID',
    contract_no VARCHAR(50) UNIQUE NOT NULL COMMENT '合同编号',
    supplier_id INT NOT NULL COMMENT '供应商ID',
    title VARCHAR(300) COMMENT '合同标题',
    file_path VARCHAR(500) COMMENT '合同文件路径',
    ai_review_status VARCHAR(20) DEFAULT 'pending' COMMENT 'AI审查状态',
    ai_review_result JSON COMMENT 'AI审查结果',
    signed_at DATE COMMENT '签订日期',
    expiry_date DATE COMMENT '到期日期',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_contract_no (contract_no),
    INDEX idx_supplier (supplier_id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='合同表';

-- 20. 供应商风险预警表
CREATE TABLE IF NOT EXISTS supplier_risk_alerts (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '预警ID',
    supplier_id INT NOT NULL COMMENT '供应商ID',
    alert_type VARCHAR(50) COMMENT '预警类型',
    severity VARCHAR(20) COMMENT '严重程度: info/warning/critical',
    title VARCHAR(300) COMMENT '预警标题',
    content TEXT COMMENT '预警详情',
    source VARCHAR(500) COMMENT '信息来源',
    ai_suggestion TEXT COMMENT 'AI建议措施',
    is_read INT DEFAULT 0 COMMENT '是否已读',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_supplier (supplier_id),
    INDEX idx_severity (severity),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='供应商风险预警表';

-- 21. 大宗商品价格表
CREATE TABLE IF NOT EXISTS commodity_prices (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '价格ID',
    commodity_code VARCHAR(50) NOT NULL COMMENT '商品编码: CU/AL/STEEL/PLASTIC',
    commodity_name VARCHAR(100) NOT NULL COMMENT '商品名称',
    price FLOAT NOT NULL COMMENT '当前价格',
    currency VARCHAR(10) DEFAULT 'CNY' COMMENT '货币单位',
    unit VARCHAR(20) COMMENT '单位',
    change_percent FLOAT COMMENT '涨跌幅(%)',
    trend VARCHAR(20) COMMENT '趋势: up/down/stable',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_commodity (commodity_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='大宗商品价格表';

-- 22. 寻源推荐表
CREATE TABLE IF NOT EXISTS sourcing_recommendations (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '推荐ID',
    spare_part_id INT COMMENT '备件ID',
    specification TEXT COMMENT '备件规格书内容',
    recommendations JSON COMMENT '推荐供应商列表',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='寻源推荐表';

-- 23. 审批记录表
CREATE TABLE IF NOT EXISTS approval_records (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '审批ID',
    approval_no VARCHAR(50) UNIQUE NOT NULL COMMENT '审批单号',
    business_type VARCHAR(50) NOT NULL COMMENT '业务类型: requisition/transfer/contract',
    business_id INT NOT NULL COMMENT '业务ID',
    applicant_id INT COMMENT '申请人ID',
    approver_id INT COMMENT '审批人ID',
    ai_summary TEXT COMMENT 'AI审批摘要',
    ai_recommendation VARCHAR(50) COMMENT 'AI建议: approve/reject/further_check',
    ai_detail JSON COMMENT 'AI分析详情',
    approver_decision VARCHAR(20) COMMENT '审批人决策: approved/rejected',
    approver_comment TEXT COMMENT '审批意见',
    status VARCHAR(20) DEFAULT 'pending' COMMENT '状态: pending/approved/rejected',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_approval_no (approval_no),
    INDEX idx_business (business_type, business_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='审批记录表';

-- 24. 成本分析表
CREATE TABLE IF NOT EXISTS cost_analyses (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '分析ID',
    equipment_id INT NOT NULL COMMENT '设备ID',
    purchase_cost FLOAT DEFAULT 0 COMMENT '采购成本',
    total_repair_labor FLOAT DEFAULT 0 COMMENT '累计维修人工',
    total_parts_cost FLOAT DEFAULT 0 COMMENT '累计备件消耗',
    total_downtime_loss FLOAT DEFAULT 0 COMMENT '累计停机损失',
    lcc_total FLOAT DEFAULT 0 COMMENT 'LCC全生命周期成本',
    ai_health_score INT COMMENT 'AI健康度评分(0-100)',
    ai_recommendation TEXT COMMENT 'AI建议: keep/replace/maintain',
    ai_report JSON COMMENT 'AI详细报告',
    analyzed_at DATE COMMENT '分析日期',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_equipment (equipment_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='成本分析表';

-- 25. 知识文件表（参考项目）
CREATE TABLE IF NOT EXISTS knowledge_files (
    id VARCHAR(36) PRIMARY KEY COMMENT '主键ID，使用UUID格式',
    version_no INT COMMENT '版本号',
    collection_name VARCHAR(256) COMMENT '知识库集合名称',
    file_name VARCHAR(255) COMMENT '文件名称',
    file_type VARCHAR(20) COMMENT '文件类型',
    minio_path VARCHAR(1000) COMMENT 'MinIO存储路径',
    chunk_strategy VARCHAR(20) COMMENT '文档分块策略',
    description VARCHAR(255) COMMENT '文件描述',
    status VARCHAR(20) COMMENT '文件状态(active/inactive/archived等)',
    vector_status VARCHAR(20) DEFAULT 'pending' COMMENT '向量化状态',
    chunk_count INT DEFAULT 0 COMMENT '向量块数',
    created_time DATETIME COMMENT '创建时间',
    updated_time DATETIME COMMENT '更新时间',
    created_by INT COMMENT '创建者ID',
    updated_by INT COMMENT '更新者ID',
    INDEX idx_collection (collection_name),
    INDEX idx_status (status),
    INDEX idx_vector_status (vector_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='知识文件存储表';

-- 26. 文档分块表（参考项目）
CREATE TABLE IF NOT EXISTS document_chunks (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '自增主键',
    file_id VARCHAR(36) NOT NULL COMMENT '关联knowledge_files.id',
    chunk_index INT NOT NULL COMMENT '块序号(从0开始)',
    chunk_text TEXT COMMENT '文本块内容',
    chunk_size INT COMMENT '块大小(字符数)',
    milvus_row_id BIGINT COMMENT 'Milvus中对应的行ID',
    vector_hex VARCHAR(32) COMMENT '128位向量十六进制表示',
    status VARCHAR(20) DEFAULT 'active' COMMENT '状态: active/deleted',
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_file_id (file_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='文档分块向量记录表';
