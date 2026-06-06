"""
init_data.py - 演示数据初始化
Usage: py -3 -m app.init_data
"""
import asyncio
import json
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import async_session_factory
from app.core.security import hash_password
from app.models import (
    User, SkillRecord, ExamRecord,
    Equipment, BOMItem,
    WorkOrder, InspectionRecord, MaintenancePlan,
    SparePart, Warehouse, InventoryRecord, Requisition, TransferOrder, StagnantAlert,
    Supplier, SupplierCategory, Quotation, PriceComparison, Contract, SupplierRiskAlert,
    CommodityPrice, SourcingRecommendation,
    ApprovalRecord, CostAnalysis,
    EngineerDispatch,
)


async def init_users(session: AsyncSession):
    result = await session.execute(select(func.count()).select_from(User))
    count = result.scalar()
    if count > 0:
        print(f"[SKIP] 用户表已有 {count} 条记录")
        result = await session.execute(select(User))
        return result.scalars().all()

    users = [
        User(用户名="admin", 密码哈希=hash_password("admin123"), 真实姓名="系统管理员", 邮箱="admin@eam.com", 手机号="13800000001", 角色="admin", 是否激活=True),
        User(用户名="engineer1", 密码哈希=hash_password("123456"), 真实姓名="张工", 邮箱="zhang@eam.com", 手机号="13800000002", 角色="engineer", 是否激活=True),
        User(用户名="engineer2", 密码哈希=hash_password("123456"), 真实姓名="李工", 邮箱="li@eam.com", 手机号="13800000003", 角色="engineer", 是否激活=True),
        User(用户名="engineer3", 密码哈希=hash_password("123456"), 真实姓名="王工", 邮箱="wang@eam.com", 手机号="13800000004", 角色="engineer", 是否激活=True),
        User(用户名="supervisor1", 密码哈希=hash_password("123456"), 真实姓名="赵主管", 邮箱="zhao@eam.com", 手机号="13800000005", 角色="supervisor", 是否激活=True),
        User(用户名="purchaser1", 密码哈希=hash_password("123456"), 真实姓名="刘采购", 邮箱="liu@eam.com", 手机号="13800000006", 角色="purchaser", 是否激活=True),
        User(用户名="leader1", 密码哈希=hash_password("123456"), 真实姓名="陈领导", 邮箱="chen@eam.com", 手机号="13800000007", 角色="leader", 是否激活=True),
    ]
    for u in users:
        session.add(u)
    await session.flush()
    print(f"[OK] 插入 {len(users)} 个用户")
    return users


async def init_skill_records(session: AsyncSession, users: list):
    engineers = [u for u in users if u.角色 == "engineer"]
    records = []
    for eng in engineers:
        for skill, score in [("电气", 85), ("机械", 78), ("液压", 72), ("PLC", 80), ("安全规范", 90)]:
            records.append(SkillRecord(用户ID=eng.id, 技能维度=skill, 技能评分=score))
    for r in records:
        session.add(r)
    await session.flush()
    print(f"[OK] 插入 {len(records)} 条技能记录")


async def init_exam_records(session: AsyncSession, users: list):
    engineers = [u for u in users if u.角色 == "engineer"]
    records = [
        ExamRecord(用户ID=engineers[0].id, 考核类型="virtual_fault", 考核场景="电机轴承异响", 总得分=88, 考核详情=json.dumps({"q1": "轴承磨损", "q2": "润滑不足"}), 状态="completed"),
        ExamRecord(用户ID=engineers[1].id, 考核类型="dialogue", 考核场景="液压压力偏低", 总得分=75, 考核详情=json.dumps({"q1": "泵体泄漏", "q2": "溢流阀故障"}), 状态="completed"),
        ExamRecord(用户ID=engineers[2].id, 考核类型="virtual_fault", 考核场景="PLC程序异常", 总得分=92, 考核详情=json.dumps({"q1": "逻辑错误", "q2": "IO模块故障"}), 状态="completed"),
    ]
    for r in records:
        session.add(r)
    await session.flush()
    print(f"[OK] 插入 {len(records)} 条考核记录")


async def init_equipments(session: AsyncSession):
    equipments = [
        Equipment(设备编码="EQ-001", 设备名称="数控车床 CK6140", 设备型号="CK6140", 设备分类="机加工", 所属厂区="F01", 所属车间="机加工", 所属产线="A", 设备状态="running", 采购日期="2022-03-15", 质保到期日="2025-03-15", 制造商="沈阳机床", 供应商ID=1),
        Equipment(设备编码="EQ-002", 设备名称="加工中心 VMC850", 设备型号="VMC850", 设备分类="机加工", 所属厂区="F01", 所属车间="机加工", 所属产线="B", 设备状态="running", 采购日期="2021-06-20", 质保到期日="2024-06-20", 制造商="大连机床", 供应商ID=2),
        Equipment(设备编码="EQ-003", 设备名称="注塑机 HTF200", 设备型号="HTF200", 设备分类="注塑", 所属厂区="F02", 所属车间="注塑", 所属产线="C", 设备状态="maintenance", 采购日期="2020-09-10", 质保到期日="2023-09-10", 制造商="海天", 供应商ID=3),
        Equipment(设备编码="EQ-004", 设备名称="焊接机器人 IRB2600", 设备型号="IRB2600", 设备分类="机器人", 所属厂区="F01", 所属车间="焊接", 所属产线="D", 设备状态="running", 采购日期="2023-01-05", 质保到期日="2026-01-05", 制造商="ABB", 供应商ID=4),
        Equipment(设备编码="EQ-005", 设备名称="空压机 GA75", 设备型号="GA75", 设备分类="动力", 所属厂区="F03", 所属车间="动力", 所属产线="公用", 设备状态="running", 采购日期="2019-11-20", 质保到期日="2022-11-20", 制造商="阿特拉斯", 供应商ID=5),
    ]
    for e in equipments:
        session.add(e)
    await session.flush()
    print(f"[OK] 插入 {len(equipments)} 台设备")
    return equipments


async def init_spare_parts(session: AsyncSession):
    parts = [
        SparePart(SKU编码="SP-001", 备件名称="主轴轴承 6208", 规格型号="6208-2RS 40x80x18mm", 分类="轴承", 单位="个", 参考单价=45.0, 最小库存=5, 最大库存=50, 安全库存=10),
        SparePart(SKU编码="SP-002", 备件名称="伺服驱动器", 规格型号="ASD-B2-0721-B 750W", 分类="电气", 单位="套", 参考单价=1200.0, 最小库存=2, 最大库存=20, 安全库存=3),
        SparePart(SKU编码="SP-003", 备件名称="液压泵", 规格型号="PV2R1-17-F-RAA-43", 分类="液压", 单位="套", 参考单价=850.0, 最小库存=2, 最大库存=15, 安全库存=3),
        SparePart(SKU编码="SP-004", 备件名称="PLC模块 SM322", 规格型号="6ES7322-1BL00-0AA0", 分类="PLC", 单位="个", 参考单价=680.0, 最小库存=3, 最大库存=30, 安全库存=5),
        SparePart(SKU编码="SP-005", 备件名称="空气滤芯", 规格型号="GA75 1613950300", 分类="滤芯", 单位="个", 参考单价=320.0, 最小库存=4, 最大库存=40, 安全库存=8),
        SparePart(SKU编码="SP-006", 备件名称="机器人伺服电机", 规格型号="IRB2600 3HAC17484-10", 分类="机器人", 单位="套", 参考单价=5600.0, 最小库存=1, 最大库存=5, 安全库存=1),
    ]
    for p in parts:
        session.add(p)
    await session.flush()
    print(f"[OK] 插入 {len(parts)} 个备件")
    return parts


async def init_bom_items(session: AsyncSession, equipments: list, parts: list):
    boms = [
        BOMItem(设备ID=equipments[0].id, 备件ID=parts[0].id, 标准用量=2, 是否关键备件=1, 安装位置="主轴箱", AI置信度=0.95),
        BOMItem(设备ID=equipments[0].id, 备件ID=parts[1].id, 标准用量=1, 是否关键备件=1, 安装位置="电气柜", AI置信度=0.92),
        BOMItem(设备ID=equipments[1].id, 备件ID=parts[0].id, 标准用量=4, 是否关键备件=1, 安装位置="主轴", AI置信度=0.94),
        BOMItem(设备ID=equipments[2].id, 备件ID=parts[2].id, 标准用量=1, 是否关键备件=1, 安装位置="液压站", AI置信度=0.93),
        BOMItem(设备ID=equipments[3].id, 备件ID=parts[5].id, 标准用量=6, 是否关键备件=1, 安装位置="关节轴", AI置信度=0.96),
        BOMItem(设备ID=equipments[4].id, 备件ID=parts[4].id, 标准用量=1, 是否关键备件=1, 安装位置="进气口", AI置信度=0.91),
    ]
    for b in boms:
        session.add(b)
    await session.flush()
    print(f"[OK] 插入 {len(boms)} 条BOM记录")


async def init_work_orders(session: AsyncSession, equipments: list, users: list):
    engineers = [u for u in users if u.角色 == "engineer"]
    orders = [
        WorkOrder(工单号="WO-202406-001", 设备ID=equipments[0].id, 故障现象="主轴异响，温度升高", 故障原因="轴承磨损，润滑不足", AI诊断置信度=0.92, 处理措施="更换主轴轴承，清洗润滑系统", 更换备件列表=json.dumps([{"sku": "SP-001", "qty": 2}]), 耗时分钟=180, 语音转译文本="主轴异响严重，需更换轴承", 工单状态="completed", 维修人员ID=engineers[0].id, 创建人ID=engineers[0].id),
        WorkOrder(工单号="WO-202406-002", 设备ID=equipments[2].id, 故障现象="液压压力低，动作缓慢", 故障原因="液压泵叶片磨损，内泄漏", AI诊断置信度=0.88, 处理措施="更换液压泵，清洗油箱，换油", 更换备件列表=json.dumps([{"sku": "SP-003", "qty": 1}]), 耗时分钟=240, 语音转译文本="液压压力上不去，泵可能损坏", 工单状态="completed", 维修人员ID=engineers[1].id, 创建人ID=engineers[1].id),
        WorkOrder(工单号="WO-202406-003", 设备ID=equipments[3].id, 故障现象="机器人第6轴定位偏差", 故障原因="伺服电机编码器故障", AI诊断置信度=0.85, 处理措施="更换伺服电机，重新校准零点", 更换备件列表=json.dumps([{"sku": "SP-006", "qty": 1}]), 耗时分钟=300, 工单状态="in_progress", 维修人员ID=engineers[2].id, 创建人ID=engineers[2].id),
        WorkOrder(工单号="WO-202406-004", 设备ID=equipments[1].id, 故障现象="加工精度下降，尺寸超差", 故障原因="滚珠丝杠间隙增大", AI诊断置信度=0.80, 处理措施="调整丝杠预紧，补偿反向间隙", 耗时分钟=120, 工单状态="pending", 创建人ID=engineers[0].id),
    ]
    for o in orders:
        session.add(o)
    await session.flush()
    print(f"[OK] 插入 {len(orders)} 条工单")
    return orders


async def init_inspection_records(session: AsyncSession, equipments: list, users: list):
    engineers = [u for u in users if u.角色 == "engineer"]
    records = [
        InspectionRecord(设备ID=equipments[0].id, 巡检人员ID=engineers[0].id, 巡检路线="机加工A线", NFC标签="NFC-F01-A01", 是否正常=1),
        InspectionRecord(设备ID=equipments[2].id, 巡检人员ID=engineers[1].id, 巡检路线="注塑C线", NFC标签="NFC-F02-C01", 是否正常=0, 异常描述="液压油温过高，75℃", 异常照片="https://minio.eam.com/inspection/IMG001.jpg"),
        InspectionRecord(设备ID=equipments[4].id, 巡检人员ID=engineers[0].id, 巡检路线="动力公用", NFC标签="NFC-F03-P01", 是否正常=1),
    ]
    for r in records:
        session.add(r)
    await session.flush()
    print(f"[OK] 插入 {len(records)} 条巡检记录")


async def init_maintenance_plans(session: AsyncSession, equipments: list):
    plans = [
        MaintenancePlan(设备ID=equipments[0].id, 计划类型="preventive", 预测失效时间="2024-12-15", AI预测描述="主轴轴承预计12月达到磨损极限", AI建议措施="11月底前安排预防性更换", 建议更换备件="主轴轴承 6208", 计划状态="pending"),
        MaintenancePlan(设备ID=equipments[2].id, 计划类型="predictive", 预测失效时间="2024-07-20", AI预测描述="液压泵振动频谱异常，预计30天内失效", AI建议措施="立即采购备件，安排停机检修", 建议更换备件="液压泵 PV2R1-17", 计划状态="pending"),
        MaintenancePlan(设备ID=equipments[4].id, 计划类型="preventive", 预测失效时间="2024-08-10", AI预测描述="空气滤芯压差接近报警值", AI建议措施="8月初更换滤芯", 建议更换备件="空气滤芯 1613950300", 计划状态="pending"),
    ]
    for p in plans:
        session.add(p)
    await session.flush()
    print(f"[OK] 插入 {len(plans)} 条维护计划")


async def init_warehouses(session: AsyncSession, users: list):
    supervisor = next(u for u in users if u.角色 == "supervisor")
    warehouses = [
        Warehouse(仓库编码="WH-01", 仓库名称="机加工备件库", 所属厂区="F01", 地址="1号厂房东侧", 负责人ID=supervisor.id),
        Warehouse(仓库编码="WH-02", 仓库名称="注塑备件库", 所属厂区="F02", 地址="2号厂房南侧", 负责人ID=supervisor.id),
        Warehouse(仓库编码="WH-03", 仓库名称="电气元件库", 所属厂区="F01", 地址="1号厂房西侧", 负责人ID=supervisor.id),
        Warehouse(仓库编码="WH-04", 仓库名称="通用备件库", 所属厂区="F03", 地址="3号厂房北侧", 负责人ID=supervisor.id),
    ]
    for w in warehouses:
        session.add(w)
    await session.flush()
    print(f"[OK] 插入 {len(warehouses)} 个仓库")
    return warehouses


async def init_inventory_records(session: AsyncSession, parts: list, warehouses: list):
    records = [
        InventoryRecord(备件ID=parts[0].id, 仓库ID=warehouses[0].id, 库位编码="A-01-03", 账面数量=25, 可用数量=20, 预留数量=5, 预留用途="WO-202406-001", 批次号="B20240315", 生产日期=datetime(2024, 3, 15), 过期日期=datetime(2029, 3, 15)),
        InventoryRecord(备件ID=parts[1].id, 仓库ID=warehouses[2].id, 库位编码="B-02-01", 账面数量=8, 可用数量=8, 预留数量=0, 批次号="B20240220", 生产日期=datetime(2024, 2, 20)),
        InventoryRecord(备件ID=parts[2].id, 仓库ID=warehouses[1].id, 库位编码="C-01-05", 账面数量=5, 可用数量=3, 预留数量=2, 预留用途="WO-202406-002", 批次号="B20240110", 生产日期=datetime(2024, 1, 10)),
        InventoryRecord(备件ID=parts[3].id, 仓库ID=warehouses[2].id, 库位编码="B-03-02", 账面数量=15, 可用数量=15, 预留数量=0, 批次号="B20240501", 生产日期=datetime(2024, 5, 1)),
        InventoryRecord(备件ID=parts[4].id, 仓库ID=warehouses[3].id, 库位编码="D-01-01", 账面数量=30, 可用数量=28, 预留数量=2, 预留用途="计划性维护", 批次号="B20240401", 生产日期=datetime(2024, 4, 1)),
        InventoryRecord(备件ID=parts[5].id, 仓库ID=warehouses[0].id, 库位编码="A-05-02", 账面数量=3, 可用数量=3, 预留数量=0, 批次号="B20240301", 生产日期=datetime(2024, 3, 1)),
    ]
    for r in records:
        session.add(r)
    await session.flush()
    print(f"[OK] 插入 {len(records)} 条库存记录")


async def init_requisitions(session: AsyncSession, parts: list, users: list, work_orders: list):
    engineers = [u for u in users if u.角色 == "engineer"]
    reqs = [
        Requisition(申购单号="REQ-202406-001", 备件ID=parts[0].id, 申请人ID=engineers[0].id, 申请数量=10, AI推荐数量=8, AI推荐理由="当前库存25，未来3个月需求约8", AI审核状态="pass", 关联工单ID=work_orders[0].id, 申购状态="pending"),
        Requisition(申购单号="REQ-202406-002", 备件ID=parts[2].id, 申请人ID=engineers[1].id, 申请数量=5, AI推荐数量=3, AI推荐理由="当前库存5，但2个已预留", AI审核状态="warning", 偏离原因="预防性备货", 关联工单ID=work_orders[1].id, 申购状态="pending"),
        Requisition(申购单号="REQ-202406-003", 备件ID=parts[4].id, 申请人ID=engineers[0].id, 申请数量=20, AI推荐数量=15, AI推荐理由="滤芯为消耗品，建议批量采购", AI审核状态="pass", 申购状态="approved"),
    ]
    for r in reqs:
        session.add(r)
    await session.flush()
    print(f"[OK] 插入 {len(reqs)} 条申购单")


async def init_transfer_orders(session: AsyncSession, parts: list, warehouses: list):
    transfers = [
        TransferOrder(调拨单号="TRF-202406-001", 备件ID=parts[0].id, 调出仓库ID=warehouses[0].id, 调入仓库ID=warehouses[1].id, 调拨数量=5, AI可行性打分=85.0, 调拨总成本=120.0, 缺货停工等待成本=500.0, 净收益=380.0, AI建议="建议调拨，净收益380", 调拨状态="completed"),
        TransferOrder(调拨单号="TRF-202406-002", 备件ID=parts[3].id, 调出仓库ID=warehouses[2].id, 调入仓库ID=warehouses[0].id, 调拨数量=3, AI可行性打分=72.0, 调拨总成本=80.0, 缺货停工等待成本=200.0, 净收益=120.0, AI建议="建议调拨", 调拨状态="in_transit"),
    ]
    for t in transfers:
        session.add(t)
    await session.flush()
    print(f"[OK] 插入 {len(transfers)} 条调拨单")


async def init_stagnant_alerts(session: AsyncSession, parts: list, warehouses: list):
    alerts = [
        StagnantAlert(备件ID=parts[1].id, 仓库ID=warehouses[2].id, 呆滞数量=3, 呆滞天数=180, AI预测即将呆滞天数=30, AI处理建议="建议调拨至机加工车间或退库", 调拨建议=json.dumps({"to": "WH-01", "qty": 3}), 预警状态="active"),
        StagnantAlert(备件ID=parts[5].id, 仓库ID=warehouses[0].id, 呆滞数量=1, 呆滞天数=120, AI预测即将呆滞天数=60, AI处理建议="机器人伺服电机周转慢，建议退供应商", 预警状态="active"),
    ]
    for a in alerts:
        session.add(a)
    await session.flush()
    print(f"[OK] 插入 {len(alerts)} 条呆滞预警")


async def init_suppliers(session: AsyncSession):
    suppliers = [
        Supplier(供应商编码="SUP-001", 供应商名称="沈阳机床配件有限公司", 联系人="王经理", 联系电话="13912345678", 邮箱="wang@symt.com", 地址="沈阳铁西", 交付准时率=95.0, 质量合格率=98.0, 综合评分=92.0, 风险等级="low", 风险标签=json.dumps(["稳定", "长期合作"])),
        Supplier(供应商编码="SUP-002", 供应商名称="大连精密机械厂", 联系人="李经理", 联系电话="13987654321", 邮箱="li@dljm.com", 地址="大连甘井子", 交付准时率=88.0, 质量合格率=95.0, 综合评分=85.0, 风险等级="medium", 风险标签=json.dumps(["交付波动"])),
        Supplier(供应商编码="SUP-003", 供应商名称="海天配件中心", 联系人="张经理", 联系电话="13811112222", 邮箱="zhang@haitian.com", 地址="宁波北仑", 交付准时率=92.0, 质量合格率=97.0, 综合评分=90.0, 风险等级="low", 风险标签=json.dumps(["质量优", "响应快"])),
        Supplier(供应商编码="SUP-004", 供应商名称="ABB机器人配件", 联系人="赵经理", 联系电话="13833334444", 邮箱="zhao@abb.com", 地址="上海浦东", 交付准时率=98.0, 质量合格率=99.0, 综合评分=96.0, 风险等级="low", 风险标签=json.dumps(["国际品牌", "高品质"])),
        Supplier(供应商编码="SUP-005", 供应商名称="阿特拉斯代理商", 联系人="刘经理", 联系电话="13855556666", 邮箱="liu@atlascopco.com", 地址="北京朝阳", 交付准时率=90.0, 质量合格率=96.0, 综合评分=88.0, 风险等级="medium", 风险标签=json.dumps(["价格偏高"])),
    ]
    for s in suppliers:
        session.add(s)
    await session.flush()
    print(f"[OK] 插入 {len(suppliers)} 个供应商")
    return suppliers


async def init_supplier_categories(session: AsyncSession, suppliers: list):
    cats = [
        SupplierCategory(供应商ID=suppliers[0].id, 供应品类="机床配件", 是否合格=1),
        SupplierCategory(供应商ID=suppliers[0].id, 供应品类="轴承", 是否合格=1),
        SupplierCategory(供应商ID=suppliers[1].id, 供应品类="精密零件", 是否合格=1),
        SupplierCategory(供应商ID=suppliers[2].id, 供应品类="液压件", 是否合格=1),
        SupplierCategory(供应商ID=suppliers[3].id, 供应品类="机器人配件", 是否合格=1),
        SupplierCategory(供应商ID=suppliers[3].id, 供应品类="伺服电机", 是否合格=1),
        SupplierCategory(供应商ID=suppliers[4].id, 供应品类="空压机配件", 是否合格=1),
        SupplierCategory(供应商ID=suppliers[4].id, 供应品类="滤芯", 是否合格=1),
    ]
    for c in cats:
        session.add(c)
    await session.flush()
    print(f"[OK] 插入 {len(cats)} 条供应商品类")


async def init_quotations(session: AsyncSession, suppliers: list, parts: list):
    quotes = [
        Quotation(报价单号="Q-202406-001", 供应商ID=suppliers[0].id, 报价明细=json.dumps([{"sku": "SP-001", "name": "主轴轴承 6208", "qty": 10, "unit_price": 42.0, "total": 420.0}]), 原始文件路径="minio://quotations/Q001.pdf", OCR状态="success", OCR置信度=0.95, 报价状态="received"),
        Quotation(报价单号="Q-202406-002", 供应商ID=suppliers[1].id, 报价明细=json.dumps([{"sku": "SP-001", "name": "主轴轴承 6208", "qty": 10, "unit_price": 38.0, "total": 380.0}]), 原始文件路径="minio://quotations/Q002.pdf", OCR状态="success", OCR置信度=0.92, 报价状态="received"),
        Quotation(报价单号="Q-202406-003", 供应商ID=suppliers[2].id, 报价明细=json.dumps([{"sku": "SP-003", "name": "液压泵", "qty": 2, "unit_price": 820.0, "total": 1640.0}]), 原始文件路径="minio://quotations/Q003.pdf", OCR状态="success", OCR置信度=0.94, 报价状态="received"),
        Quotation(报价单号="Q-202406-004", 供应商ID=suppliers[3].id, 报价明细=json.dumps([{"sku": "SP-006", "name": "机器人伺服电机", "qty": 1, "unit_price": 5400.0, "total": 5400.0}]), 原始文件路径="minio://quotations/Q004.pdf", OCR状态="success", OCR置信度=0.96, 报价状态="received"),
    ]
    for q in quotes:
        session.add(q)
    await session.flush()
    print(f"[OK] 插入 {len(quotes)} 条报价单")


async def init_price_comparisons(session: AsyncSession, parts: list, users: list):
    purchaser = next(u for u in users if u.角色 == "purchaser")
    comps = [
        PriceComparison(比价单号="PC-202406-001", 备件ID=parts[0].id, 参与比价报价单ID列表=json.dumps([1, 2]), 比价结果=json.dumps({"winner": "SUP-002", "reason": "价格最低", "savings": 40.0}), 创建人ID=purchaser.id),
        PriceComparison(比价单号="PC-202406-002", 备件ID=parts[2].id, 参与比价报价单ID列表=json.dumps([3]), 比价结果=json.dumps({"winner": "SUP-003", "reason": "唯一报价", "savings": 0.0}), 创建人ID=purchaser.id),
    ]
    for c in comps:
        session.add(c)
    await session.flush()
    print(f"[OK] 插入 {len(comps)} 条比价记录")


async def init_contracts(session: AsyncSession, suppliers: list):
    from app.services.contract_storage import sync_contracts_to_minio

    contracts = [
        Contract(合同编号="CT-2024-001", 供应商ID=suppliers[0].id, 合同标题="2024年机床轴承采购合同", 文件路径="minio://contracts/CT001.pdf", AI审查状态="approved", AI审查结果=json.dumps({"risk_level": "low", "issues": []}), 签订日期=datetime(2024, 1, 15).date(), 到期日期=datetime(2024, 12, 31).date()),
        Contract(合同编号="CT-2024-002", 供应商ID=suppliers[3].id, 合同标题="ABB机器人年度维保合同", 文件路径="minio://contracts/CT002.pdf", AI审查状态="approved", AI审查结果=json.dumps({"risk_level": "low", "issues": []}), 签订日期=datetime(2024, 2, 1).date(), 到期日期=datetime(2025, 1, 31).date()),
        Contract(合同编号="CT-2024-003", 供应商ID=suppliers[4].id, 合同标题="空气滤芯采购合同", 文件路径="minio://contracts/CT003.pdf", AI审查状态="pending", AI审查结果=json.dumps({"risk_level": "medium", "issues": ["付款条件严格"]}), 签订日期=datetime(2024, 3, 10).date(), 到期日期=datetime(2024, 9, 10).date()),
    ]
    for c in contracts:
        session.add(c)
    await session.flush()
    stats = sync_contracts_to_minio(contracts)
    print(f"[OK] 插入 {len(contracts)} 条合同，MinIO 同步 {stats['已同步']} 个文件")


async def init_supplier_risk_alerts(session: AsyncSession, suppliers: list):
    alerts = [
        SupplierRiskAlert(供应商ID=suppliers[1].id, 预警类型="交付延迟", 严重程度="warning", 预警标题="大连精密近期交付延迟", 预警详情="近3个月平均延迟5天", 信息来源="内部统计", AI建议措施="增加安全库存或寻找备选供应商"),
        SupplierRiskAlert(供应商ID=suppliers[4].id, 预警类型="价格波动", 严重程度="info", 预警标题="空气滤芯价格上涨", 预警详情="原材料铜价上涨导致成本增加8%", 信息来源="市场行情", AI建议措施="提前锁价或批量采购"),
    ]
    for a in alerts:
        session.add(a)
    await session.flush()
    print(f"[OK] 插入 {len(alerts)} 条供应商风险预警")


async def init_commodity_prices(session: AsyncSession):
    prices = [
        CommodityPrice(商品编码="CU", 商品名称="铜", 当前价格=68000.0, 货币单位="CNY", 单位="元/吨", 涨跌幅=2.5, 趋势="up"),
        CommodityPrice(商品编码="AL", 商品名称="铝", 当前价格=18500.0, 货币单位="CNY", 单位="元/吨", 涨跌幅=-1.2, 趋势="down"),
        CommodityPrice(商品编码="STEEL", 商品名称="钢材", 当前价格=4200.0, 货币单位="CNY", 单位="元/吨", 涨跌幅=0.5, 趋势="stable"),
        CommodityPrice(商品编码="PLASTIC", 商品名称="塑料", 当前价格=8500.0, 货币单位="CNY", 单位="元/吨", 涨跌幅=3.0, 趋势="up"),
    ]
    for p in prices:
        session.add(p)
    await session.flush()
    print(f"[OK] 插入 {len(prices)} 条大宗商品价格")


async def init_sourcing_recommendations(session: AsyncSession, parts: list):
    recs = [
        SourcingRecommendation(备件ID=parts[0].id, 规格书内容="6208-2RS 40x80x18mm", 推荐供应商列表=json.dumps([{"supplier_id": 1, "supplier_name": "沈阳机床配件", "score": 92, "reason": "质量稳定"}, {"supplier_id": 2, "supplier_name": "大连精密", "score": 85, "reason": "价格优势"}])),
        SourcingRecommendation(备件ID=parts[5].id, 规格书内容="IRB2600 3HAC17484-10", 推荐供应商列表=json.dumps([{"supplier_id": 4, "supplier_name": "ABB机器人配件", "score": 96, "reason": "原厂配件"}])),
    ]
    for r in recs:
        session.add(r)
    await session.flush()
    print(f"[OK] 插入 {len(recs)} 条寻源推荐")


async def init_approval_records(session: AsyncSession, users: list):
    engineers = [u for u in users if u.角色 == "engineer"]
    purchaser = next(u for u in users if u.角色 == "purchaser")
    supervisor = next(u for u in users if u.角色 == "supervisor")
    records = [
        ApprovalRecord(审批单号="APR-202406-001", 业务类型="requisition", 业务ID=1, 申请人ID=engineers[0].id, AI审批摘要="申购数量合理，库存充足", AI建议="approve", AI分析详情=json.dumps({"budget_check": "pass", "stock_check": "sufficient"}), 审批人决策="approved", 审批意见="同意采购", 审批状态="approved"),
        ApprovalRecord(审批单号="APR-202406-002", 业务类型="requisition", 业务ID=2, 申请人ID=engineers[1].id, AI审批摘要="申购略高于AI推荐，但理由充分", AI建议="approve", AI分析详情=json.dumps({"budget_check": "warning", "stock_check": "low"}), 审批人决策="approved", 审批意见="同意，关注库存", 审批状态="approved"),
        ApprovalRecord(审批单号="APR-202406-003", 业务类型="contract", 业务ID=3, 申请人ID=purchaser.id, AI审批摘要="合同付款条件严格，建议协商", AI建议="further_check", AI分析详情=json.dumps({"risk_points": ["付款条件", "违约金"]}), 审批状态="pending"),
        ApprovalRecord(审批单号="APR-202406-004", 业务类型="transfer", 业务ID=1, 申请人ID=supervisor.id, AI审批摘要="调拨净收益380，建议执行", AI建议="approve", AI分析详情=json.dumps({"cost_benefit": "positive"}), 审批状态="pending"),
    ]
    for r in records:
        session.add(r)
    await session.flush()
    print(f"[OK] 插入 {len(records)} 条审批记录")


async def init_cost_analyses(session: AsyncSession, equipments: list):
    analyses = [
        CostAnalysis(设备ID=equipments[0].id, 采购成本=280000.0, 累计维修人工=15000.0, 累计备件消耗=8500.0, 累计停机损失=5000.0, LCC全生命周期成本=308500.0, AI健康度评分=85, AI建议="maintain", AI详细报告=json.dumps({"health": "良好", "suggestion": "继续预防性维护"}), 分析日期=datetime(2024, 6, 1).date()),
        CostAnalysis(设备ID=equipments[2].id, 采购成本=450000.0, 累计维修人工=35000.0, 累计备件消耗=22000.0, 累计停机损失=18000.0, LCC全生命周期成本=525000.0, AI健康度评分=62, AI建议="replace", AI详细报告=json.dumps({"health": "一般", "suggestion": "3年内考虑更换"}), 分析日期=datetime(2024, 6, 1).date()),
        CostAnalysis(设备ID=equipments[4].id, 采购成本=120000.0, 累计维修人工=8000.0, 累计备件消耗=12000.0, 累计停机损失=3000.0, LCC全生命周期成本=143000.0, AI健康度评分=78, AI建议="maintain", AI详细报告=json.dumps({"health": "良好", "suggestion": "按维护计划执行"}), 分析日期=datetime(2024, 6, 1).date()),
    ]
    for a in analyses:
        session.add(a)
    await session.flush()
    print(f"[OK] 插入 {len(analyses)} 条成本分析")


async def init_dispatches(session: AsyncSession, users: list):
    engineers = [u for u in users if u.角色 == "engineer"]
    supervisor = [u for u in users if u.角色 == "supervisor"][0]
    dispatches = [
        EngineerDispatch(工程师ID=engineers[0].id, 工程师姓名="张工", 工程师技能=json.dumps({"电气": 85, "机械": 78}), 维修地点="2号车间A线数控车床", 距离公里=5.2, 任务描述="主轴轴承更换", 调派状态="completed", 主管ID=supervisor.id, 主管姓名="赵主管"),
        EngineerDispatch(工程师ID=engineers[1].id, 工程师姓名="李工", 工程师技能=json.dumps({"液压": 72, "机械": 80}), 维修地点="注塑C线", 距离公里=8.5, 任务描述="液压泵更换及系统清洗", 调派状态="completed", 主管ID=supervisor.id, 主管姓名="赵主管"),
        EngineerDispatch(工程师ID=engineers[2].id, 工程师姓名="王工", 工程师技能=json.dumps({"电气": 90, "PLC": 80}), 维修地点="焊接D线", 距离公里=12.0, 任务描述="机器人第6轴伺服电机更换", 调派状态="in_progress", 主管ID=supervisor.id, 主管姓名="赵主管"),
        EngineerDispatch(工程师ID=engineers[0].id, 工程师姓名="张工", 工程师技能=json.dumps({"电气": 85, "机械": 78}), 维修地点="机加工B线", 距离公里=3.8, 任务描述="加工中心精度调整", 调派状态="dispatched", 主管ID=supervisor.id, 主管姓名="赵主管"),
    ]
    for d in dispatches:
        session.add(d)
    await session.flush()
    print(f"[OK] 插入 {len(dispatches)} 条调派记录")


async def main():
    async with async_session_factory() as session:
        try:
            print("=" * 60)
            print("开始初始化演示数据")
            print("=" * 60)

            users = await init_users(session)
            await init_skill_records(session, users)
            await init_exam_records(session, users)

            equipments = await init_equipments(session)
            parts = await init_spare_parts(session)
            await init_bom_items(session, equipments, parts)

            work_orders = await init_work_orders(session, equipments, users)
            await init_inspection_records(session, equipments, users)
            await init_maintenance_plans(session, equipments)

            warehouses = await init_warehouses(session, users)
            await init_inventory_records(session, parts, warehouses)

            await init_requisitions(session, parts, users, work_orders)
            await init_transfer_orders(session, parts, warehouses)
            await init_stagnant_alerts(session, parts, warehouses)

            suppliers = await init_suppliers(session)
            await init_supplier_categories(session, suppliers)
            await init_quotations(session, suppliers, parts)
            await init_price_comparisons(session, parts, users)
            await init_contracts(session, suppliers)
            await init_supplier_risk_alerts(session, suppliers)
            await init_commodity_prices(session)
            await init_sourcing_recommendations(session, parts)

            await init_approval_records(session, users)
            await init_cost_analyses(session, equipments)
            await init_dispatches(session, users)

            await session.commit()
            print("=" * 60)
            print("[DONE] 全部演示数据初始化完成！")
            print("=" * 60)

        except Exception as e:
            await session.rollback()
            print(f"[ERROR] 初始化失败: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(main())
