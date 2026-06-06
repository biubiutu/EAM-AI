"""合同文件路径解析与 MinIO 同步"""

CONTRACT_MINIO_PREFIX = "contracts/"


def parse_contract_object_name(文件路径: str) -> str:
    """将数据库文件路径解析为 MinIO 对象名，如 minio://contracts/CT001.pdf -> contracts/CT001.pdf"""
    if not 文件路径:
        return ""
    path = 文件路径.strip()
    if path.startswith("minio://"):
        path = path[len("minio://"):]
    return path.lstrip("/")


def build_contract_file_body(合同编号: str, 合同标题: str) -> bytes:
    content = (
        f"【演示合同文件】\n"
        f"合同编号：{合同编号}\n"
        f"合同标题：{合同标题}\n"
        f"说明：本文件由 init_data / sync_contract_minio 生成，用于与数据库记录精准匹配。\n"
    )
    return content.encode("utf-8")


def sync_contracts_to_minio(contracts: list) -> dict:
    """按合同表中的文件路径，将文件同步到 MinIO（对象名完全一致）"""
    from app.utils.minio_client import minio_client
    from app.config.settings import settings

    synced = 0
    skipped = 0
    errors: list[str] = []
    for c in contracts:
        obj = parse_contract_object_name(getattr(c, "文件路径", "") or "")
        if not obj or not obj.startswith(CONTRACT_MINIO_PREFIX):
            skipped += 1
            continue
        try:
            body = build_contract_file_body(c.合同编号, c.合同标题 or "")
            minio_client.put_object_exact(body, obj, bucket=settings.KB_BUCKET_NAME)
            synced += 1
        except Exception as e:
            errors.append(f"{c.合同编号}: {e}")
    return {"已同步": synced, "已跳过": skipped, "错误": errors}
