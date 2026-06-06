"""插入报价单与比价记录演示数据（中文表/列名）"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pymysql
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "123456")
MYSQL_DB = os.getenv("MYSQL_DB", "eam_ai")

SUPPLIERS = [
    ("SUP-001", "沈阳机床配件有限公司", "王经理", "13912345678"),
    ("SUP-002", "大连精密机械厂", "李经理", "13987654321"),
    ("SUP-003", "海天配件中心", "张经理", "13811112222"),
]

QUOTATIONS = [
    ("Q-202406-001", 1, [
        {"备件名称": "主轴轴承6208", "规格型号": "6208-2RS", "单价": 42.0, "数量": 10, "总价": 420.0,
         "币种": "CNY", "交期天数": 7, "付款条件": "月结30天", "含税": "是"},
    ], "minio://quotations/Q001.pdf", 0.95),
    ("Q-202406-002", 2, [
        {"备件名称": "主轴轴承6208", "规格型号": "6208-2RS", "单价": 38.0, "数量": 10, "总价": 380.0,
         "币种": "CNY", "交期天数": 10, "付款条件": "货到付款", "含税": "是"},
    ], "minio://quotations/Q002.pdf", 0.92),
    ("Q-202406-003", 3, [
        {"备件名称": "液压泵", "规格型号": "PV2R1-17", "单价": 820.0, "数量": 2, "总价": 1640.0,
         "币种": "CNY", "交期天数": 14, "付款条件": "预付30%", "含税": "是"},
    ], "minio://quotations/Q003.pdf", 0.94),
]

COMPARISON = {
    "比价单号": "PC-202406-001",
    "备件ID": 1,
    "参与比价报价单ID列表": [1, 2],
    "比价结果": {
        "备件名称": "主轴轴承6208",
        "推荐供应商ID": 2,
        "推荐理由": "大连精密机械厂单价最低(¥38/个)，综合得分最高，交期可接受",
        "维度评分": {
            "价格": {"rank": 1, "score": 92, "details": "三家报价中单价最低"},
            "交期": {"rank": 2, "score": 85, "details": "10天交期，略长于最快供应商"},
            "付款条件": {"rank": 2, "score": 80, "details": "货到付款，资金压力较小"},
            "质量历史": {"rank": 2, "score": 88, "details": "质量合格率95%"},
        },
        "汇总表": [
            {"供应商ID": 1, "供应商名称": "沈阳机床配件有限公司", "单价": 42.0, "交期天数": 7, "付款条件": "月结30天", "综合得分": 86},
            {"供应商ID": 2, "供应商名称": "大连精密机械厂", "单价": 38.0, "交期天数": 10, "付款条件": "货到付款", "综合得分": 91},
            {"供应商ID": 3, "供应商名称": "海天配件中心", "单价": 45.0, "交期天数": 5, "付款条件": "月结60天", "综合得分": 82},
        ],
        "谈判建议": [
            "可要求大连精密机械厂将交期缩短至7天以换取批量订单",
            "沈阳机床配件有限公司付款条件较优，可作为备选供应商",
        ],
    },
    "创建人ID": 1,
}


def main() -> None:
    conn = pymysql.connect(
        host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER,
        password=MYSQL_PASSWORD, database=MYSQL_DB, charset="utf8mb4",
    )
    cur = conn.cursor()

    for code, name, contact, phone in SUPPLIERS:
        cur.execute("SELECT id FROM `供应商` WHERE `供应商编码`=%s", (code,))
        if not cur.fetchone():
            cur.execute(
                "INSERT INTO `供应商` (`供应商编码`, `供应商名称`, `联系人`, `联系电话`, "
                "`交付准时率`, `质量合格率`, `综合评分`, `风险等级`) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                (code, name, contact, phone, 90.0, 96.0, 88.0, "low"),
            )
            print(f"[OK] 供应商 {name}")

    for qno, sid, items, path, conf in QUOTATIONS:
        cur.execute("SELECT id FROM `报价单` WHERE `报价单号`=%s", (qno,))
        if cur.fetchone():
            continue
        cur.execute(
            "INSERT INTO `报价单` (`报价单号`, `供应商ID`, `报价明细`, `原始文件路径`, "
            "`OCR状态`, `OCR置信度`, `报价状态`) VALUES (%s,%s,%s,%s,%s,%s,%s)",
            (qno, sid, json.dumps(items, ensure_ascii=False), path, "success", conf, "received"),
        )
        print(f"[OK] 报价单 {qno}")

    cur.execute("SELECT id FROM `比价记录` WHERE `比价单号`=%s", (COMPARISON["比价单号"],))
    if not cur.fetchone():
        cur.execute(
            "INSERT INTO `比价记录` (`比价单号`, `备件ID`, `参与比价报价单ID列表`, "
            "`比价结果`, `创建人ID`) VALUES (%s,%s,%s,%s,%s)",
            (
                COMPARISON["比价单号"],
                COMPARISON["备件ID"],
                json.dumps(COMPARISON["参与比价报价单ID列表"]),
                json.dumps(COMPARISON["比价结果"], ensure_ascii=False),
                COMPARISON["创建人ID"],
            ),
        )
        print(f"[OK] 比价记录 {COMPARISON['比价单号']}")

    conn.commit()
    cur.execute("SELECT COUNT(*) FROM `报价单`")
    q_cnt = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM `比价记录`")
    c_cnt = cur.fetchone()[0]
    print(f"完成：报价单 {q_cnt} 条，比价记录 {c_cnt} 条")
    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
