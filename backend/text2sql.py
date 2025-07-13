from database import get_session
import dashscope
import os
import re
from dotenv import load_dotenv
from sqlalchemy import text

load_dotenv()
# 设置阿里百炼API密钥
dashscope.api_key = os.getenv('DASHSCOPE_API_KEY')

def text_to_sql(natural_language_query):
    """将自然语言查询转换为SQL"""
    prompt = f"""
    你是一个医疗美容数据分析专家，需要将用户的问题转换为SQL查询语句。
    数据库结构如下：
    
    表: customers
    字段: customer_id, name, phone, register_date, last_visit_date, consultant_id, health_tags, membership_level
    
    表: consultants
    字段: consultant_id, name, department
    
    表: medical_products
    字段: product_id, product_name, department, product_type, standard_price
    
    表: consumption_records
    字段: record_id, customer_id, consume_date, amount, department, is_new_customer, consultant_id, product_id, quantity, payment_method
    
    表: write_off_records
    字段: write_off_id, customer_id, write_off_date, amount, department, product_id, quantity, consultant_id, consume_record_id
    
    表: unspent_balances
    字段: balance_id, customer_id, product_id, total_amount, spent_amount, remaining_amount, last_write_off_date, expiration_date
    
    关系说明:
    - customers 和 consumption_records 是一对多关系
    - customers 和 write_off_records 是一对多关系
    - medical_products 和 consumption_records 是一对多关系
    - consumption_records 和 write_off_records 是一对多关系
    
    请将以下自然语言查询转换为精确的SQL语句:
    "{natural_language_query}"
    
    注意:
    1. 只返回SQL语句，不要包含其他内容
    2. 使用表别名提高可读性
    3. 优先使用JOIN而不是子查询
    4. 日期处理请用SQLite语法，如 date('now', '-6 months')，不要用MySQL的DATE_SUB或INTERVAL
    5. customers 表没有 department 字段，department 字段在 consumption_records 或 medical_products 表。
    """
    
    try:
        # 检查API密钥
        api_key = os.getenv('DASHSCOPE_API_KEY')
        if not api_key:
            return "SQL生成错误: 未设置 DASHSCOPE_API_KEY 环境变量"
        
        response = dashscope.Generation.call(
            model='qwen-max',
            messages=[
                {"role": "system", "content": "你是一个专业的SQL工程师，擅长将业务问题转换为精确的SQL查询。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        
        # 检查响应是否为空
        if response is None:
            return "SQL生成错误: API响应为空"
        
        # 检查响应状态
        if hasattr(response, 'status_code') and response.status_code == 200:
            if hasattr(response, 'output') and response.output is not None:
                # 阿里百炼API返回的内容在text字段中
                if hasattr(response.output, 'text') and response.output.text is not None:
                    sql = response.output.text.strip()
                else:
                    return "SQL生成错误: API响应中没有text字段"
            else:
                return "SQL生成错误: API响应中没有output字段"
        else:
            error_msg = getattr(response, 'message', '未知错误')
            return f"SQL生成错误: {error_msg}"
        
        # 清理可能存在的代码块标记
        if sql.startswith("```sql") and sql.endswith("```"):
            sql = sql[6:-3].strip()
        elif sql.startswith("```") and sql.endswith("```"):
            sql = sql[3:-3].strip()
        
        return sql
    except Exception as e:
        return f"SQL生成错误: {str(e)}"

def execute_sql_query(sql):
    """执行SQL查询并返回结果"""
    session = get_session()
    try:
        result = session.execute(text(sql))
        columns = result.keys()
        data = result.fetchall()
        return columns, data
    except Exception as e:
        return None, f"SQL执行错误: {str(e)}"
    finally:
        session.close()

def natural_language_query(query):
    """端到端的自然语言查询处理"""
    sql = text_to_sql(query)
    
    if sql.startswith("SQL生成错误"):
        return {"success": False, "error": sql, "sql": None}
    
    columns, data = execute_sql_query(sql)
    
    if isinstance(data, str):  # 错误情况
        return {"success": False, "error": data, "sql": sql}
    
    # 转换为字典列表格式
    results = [dict(zip(columns, row)) for row in data]
    return {"success": True, "data": results, "sql": sql} 