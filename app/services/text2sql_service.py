"""
Text2SQL 服务 - 基于 Vanna 的真实 Text2SQL
"""
import json
import logging
from app.config.settings import settings
from app.utils.ai_client import ai_client
from app.services.vanna_training_service import vanna_training_service

logger = logging.getLogger(__name__)


class Text2SQLService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

    async def query(self, natural_query: str) -> dict:
        """
        自然语言 → SQL → 执行 → 返回结果
        """
        # 1. 获取 DDL
        ddl = vanna_training_service.generate_ddl()

        # 2. AI 生成 SQL
        sql = await self._generate_sql(natural_query, ddl)

        # 3. 执行 SQL
        result = await self._execute_sql(sql)

        # 4. AI 回答
        answer = await self._generate_answer(natural_query, sql, result)

        return {
            "sql": sql,
            "data": result,
            "answer": answer,
        }

    async def _generate_sql(self, query: str, ddl: str) -> str:
        """AI 生成 SQL"""
        prompt = f"""你是一个精通 SQL 的数据分析师。根据数据库DDL，将用户问题翻译为SQL语句。

【数据库DDL】
{ddl[:3000]}

【用户问题】
{query}

要求：
- 只输出 SQL 语句，不要解释
- 使用 MySQL 语法
- 表名为中文，查询时用反引号包裹
- 如果无法翻译，输出 -- 无法生成SQL
"""
        result = await ai_client.chat(prompt, temperature=0.1)
        # 清理 markdown 代码块
        result = result.strip()
        if result.startswith("```"):
            result = result.split("\n", 1)[1] if "\n" in result else result
            result = result.rsplit("```", 1)[0] if "```" in result else result
        return result.strip()

    async def _execute_sql(self, sql: str) -> list[dict]:
        """执行 SQL 并返回结果"""
        if not sql or sql.startswith("--"):
            return [{"message": "无法为当前问题生成有效 SQL"}]

        try:
            import sqlalchemy as sa
            engine = sa.create_engine(settings.MYSQL_URL)
            with engine.connect() as conn:
                result = conn.execute(sa.text(sql))
                columns = result.keys()
                rows = result.fetchmany(100)
                data = [dict(zip(columns, row)) for row in rows]
                return data
        except Exception as e:
            logger.warning("SQL 执行失败: %s", e)
            return [{"error": str(e)}]

    async def _generate_answer(self, query: str, sql: str, data: list[dict]) -> str:
        """AI 根据查询结果生成自然语言回答"""
        prompt = f"""你是数据分析助手。根据用户问题、SQL 和查询结果生成简洁回答。

【用户问题】
{query}

【SQL】
{sql}

【查询结果】
{json.dumps(data[:20], ensure_ascii=False, indent=2)}

请用中文简洁回答用户问题，如果查询出错，说明原因。
"""
        return await ai_client.chat(prompt, temperature=0.5)


text2sql_service = Text2SQLService()