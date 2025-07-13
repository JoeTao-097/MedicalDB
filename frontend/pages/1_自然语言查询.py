import streamlit as st
import requests
import pandas as pd
import json

st.set_page_config(page_title="自然语言查询", page_icon="🔍")

st.title("🔍 自然语言查询")

# API基础URL
API_BASE_URL = "http://localhost:8000"

def make_api_request(endpoint, method="GET", data=None):
    """发送API请求"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API请求错误: {str(e)}")
        return None

# 示例查询
example_queries = [
    "查询最近6个月没有消费的顾客",
    "统计每个科室2024年的总消费金额",
    "找出购买了玻尿酸但从未消费过皮肤科项目的顾客",
    "计算钻石会员的平均消费金额",
    "找出未划扣余额超过5000元的顾客",
    "统计每个咨询师的客户数量",
    "查询消费金额最高的前10位顾客",
    "分析各科室的客户满意度"
]

st.markdown("""
### 使用说明
1. 在下方输入框中输入您的问题
2. 系统会自动将自然语言转换为SQL查询
3. 查询结果将以表格形式显示
4. 您也可以选择预设的示例查询
""")

# 选择示例查询
st.subheader("📝 示例查询")
selected_example = st.selectbox("选择示例查询", ["自定义查询"] + example_queries)

# 查询输入
st.subheader("🔍 输入查询")
if selected_example == "自定义查询":
    query = st.text_area("请输入您的查询问题", height=100, placeholder="例如：查询最近6个月没有消费的顾客")
else:
    query = st.text_area("查询问题", value=selected_example, height=100)

# 查询参数
col1, col2 = st.columns(2)
with col1:
    limit = st.number_input("结果限制数量", min_value=10, max_value=1000, value=100, step=10)
with col2:
    show_sql = st.checkbox("显示生成的SQL", value=True)

# 执行查询
if st.button("🚀 执行查询", type="primary"):
    if query.strip():
        with st.spinner("正在处理查询..."):
            # 发送查询请求
            query_data = {
                "query": query,
                "limit": limit
            }
            
            result = make_api_request("/api/query", method="POST", data=query_data)
            
            if result:
                if result.get('success'):
                    st.success("查询执行成功！")
                    
                    # 显示SQL（如果启用）
                    if show_sql and result.get('sql'):
                        with st.expander("📋 生成的SQL"):
                            st.code(result['sql'], language='sql')
                    
                    # 显示结果
                    if result.get('data'):
                        st.subheader("📊 查询结果")
                        
                        # 转换为DataFrame
                        df = pd.DataFrame(result['data'])
                        
                        # 显示统计信息
                        st.info(f"共找到 {len(df)} 条记录")
                        
                        # 显示数据表格
                        st.dataframe(df, use_container_width=True)
                        
                        # 下载功能
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="📥 下载查询结果",
                            data=csv,
                            file_name=f"query_result_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                        
                        # 简单的数据可视化
                        if len(df) > 0:
                            st.subheader("📈 数据可视化")
                            
                            # 选择可视化列
                            numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
                            if numeric_columns:
                                selected_column = st.selectbox("选择要可视化的数值列", numeric_columns)
                                
                                if selected_column:
                                    col1, col2 = st.columns(2)
                                    
                                    with col1:
                                        st.bar_chart(df[selected_column])
                                    
                                    with col2:
                                        st.line_chart(df[selected_column])
                    else:
                        st.warning("查询没有返回任何数据")
                else:
                    st.error(f"查询失败: {result.get('error', '未知错误')}")
            else:
                st.error("无法连接到API服务，请确保后端服务正在运行")
    else:
        st.warning("请输入查询问题")

# 查询历史和建议
st.subheader("💡 查询建议")
st.markdown("""
**常用查询类型：**

1. **客户分析**
   - 查询最近N个月没有消费的顾客
   - 统计各会员等级的客户数量
   - 查找消费金额最高的客户

2. **业绩分析**
   - 统计各科室的消费金额
   - 分析各咨询师的业绩表现
   - 计算产品的销售情况

3. **余额管理**
   - 查找未划扣余额较高的客户
   - 统计即将过期的余额
   - 分析余额使用情况

4. **趋势分析**
   - 按时间统计消费趋势
   - 分析新客转化率
   - 统计复购率
""")

# 数据库结构说明
with st.expander("📚 数据库结构说明"):
    st.markdown("""
    **主要数据表：**
    
    - **customers**: 顾客信息表
    - **consultants**: 咨询师信息表
    - **medical_products**: 产品信息表
    - **consumption_records**: 消费记录表
    - **write_off_records**: 划扣记录表
    - **unspent_balances**: 未划扣余额表
    
    **关键字段：**
    - customer_id: 顾客ID
    - consultant_id: 咨询师ID
    - product_id: 产品ID
    - amount: 金额
    - department: 科室
    - membership_level: 会员等级
    """) 