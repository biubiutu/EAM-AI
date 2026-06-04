"""
初始化脚本：创建MySQL数据库、表、MinIO桶
"""
import os
import sys
import pymysql
from minio import Minio
from minio.error import S3Error
from dotenv import load_dotenv

# 加载.env
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(env_path)

# MySQL配置
MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "123456")
MYSQL_DB = os.getenv("MYSQL_DB", "eam_ai")

# MinIO配置
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "127.0.0.1:9100")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "vanna-training-data")
KB_BUCKET_NAME = os.getenv("KB_BUCKET_NAME", "knowledge-base")


def init_mysql():
    print("=" * 50)
    print("初始化MySQL数据库...")
    print("=" * 50)
    
    try:
        # 先连接MySQL服务器（不指定数据库）
        conn = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            charset='utf8mb4'
        )
        cursor = conn.cursor()
        
        # 创建数据库
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DB}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"[OK] 数据库 {MYSQL_DB} 已创建或已存在")
        
        # 选择数据库
        cursor.execute(f"USE `{MYSQL_DB}`")
        print(f"[OK] 已选择数据库 {MYSQL_DB}")
        
        # 读取并执行SQL文件
        sql_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sql", "init.sql")
        if os.path.exists(sql_file):
            with open(sql_file, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # 分割SQL语句
            statements = []
            current = []
            for line in sql_content.split('\n'):
                line = line.strip()
                if not line or line.startswith('--'):
                    continue
                current.append(line)
                if line.endswith(';'):
                    statements.append(' '.join(current))
                    current = []
            
            # 执行每个语句
            for stmt in statements:
                stmt = stmt.strip()
                if stmt and not stmt.startswith('CREATE DATABASE'):
                    try:
                        cursor.execute(stmt)
                    except Exception as e:
                        if 'already exists' in str(e).lower() or 'Duplicate' in str(e):
                            pass
                        else:
                            print(f"[WARN] SQL执行警告: {e}")
            
            conn.commit()
            print("[OK] 所有表已创建")
        else:
            print(f"[WARN] 未找到SQL文件: {sql_file}")
        
        # 列出所有表
        cursor.execute(f"SHOW TABLES FROM `{MYSQL_DB}`")
        tables = cursor.fetchall()
        print(f"[OK] 数据库 {MYSQL_DB} 中共有 {len(tables)} 张表:")
        for t in tables:
            print(f"  - {t[0]}")
        
        cursor.close()
        conn.close()
        return True
    except pymysql.Error as e:
        print(f"[ERROR] MySQL初始化失败: {e}")
        return False


def init_minio():
    print("\n" + "=" * 50)
    print("初始化MinIO桶...")
    print("=" * 50)
    
    try:
        client = Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=False
        )
        
        buckets = [MINIO_BUCKET, KB_BUCKET_NAME]
        for bucket_name in buckets:
            if client.bucket_exists(bucket_name):
                print(f"[OK] 桶 {bucket_name} 已存在")
            else:
                client.make_bucket(bucket_name)
                print(f"[OK] 桶 {bucket_name} 已创建")
        
        all_buckets = client.list_buckets()
        print(f"\n[OK] MinIO中共有 {len(all_buckets)} 个桶:")
        for b in all_buckets:
            print(f"  - {b.name}")
        
        return True
    except S3Error as e:
        print(f"[ERROR] MinIO初始化失败: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] MinIO连接失败: {e}")
        return False


def main():
    print("AI-EAM 系统资源初始化")
    print("=" * 50)
    print(f"MySQL: {MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}")
    print(f"MinIO: {MINIO_ENDPOINT}")
    print("=" * 50)
    
    mysql_ok = init_mysql()
    minio_ok = init_minio()
    
    print("\n" + "=" * 50)
    print("初始化完成!")
    print(f"  MySQL: {'成功' if mysql_ok else '失败'}")
    print(f"  MinIO: {'成功' if minio_ok else '失败'}")
    print("=" * 50)


if __name__ == "__main__":
    main()
