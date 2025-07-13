import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import json

# 配置页面
st.set_page_config(
    page_title="医美数据管理系统",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API基础URL
API_BASE_URL = "http://localhost:8000"

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-message {
        color: #28a745;
        font-weight: bold;
    }
    .error-message {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def make_api_request(endpoint, method="GET", data=None):
    """发送API请求"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API请求错误: {str(e)}")
        return None

def display_dashboard():
    """显示仪表板"""
    st.markdown('<h1 class="main-header">🏥 医美数据管理系统</h1>', unsafe_allow_html=True)
    
    # 获取基础统计数据
    col1, col2, col3, col4 = st.columns(4)
    
    # 顾客总数
    customers = make_api_request("/api/customers")
    customer_count = len(customers) if customers else 0
    
    with col1:
        st.metric("顾客总数", customer_count)
    
    # 咨询师总数
    consultants = make_api_request("/api/consultants")
    consultant_count = len(consultants) if consultants else 0
    
    with col2:
        st.metric("咨询师总数", consultant_count)
    
    # 产品总数
    products = make_api_request("/api/products")
    product_count = len(products) if products else 0
    
    with col3:
        st.metric("产品总数", product_count)
    
    # 消费记录总数
    consumption_records = make_api_request("/api/consumption-records")
    record_count = len(consumption_records) if consumption_records else 0
    
    with col4:
        st.metric("消费记录总数", record_count)
    
    # 快速分析
    st.subheader("📊 快速分析")
    
    # 获取分析数据
    inactive_analysis = make_api_request("/api/analysis/inactive-customers")
    reopen_analysis = make_api_request("/api/analysis/new-customer-reopen")
    vip_analysis = make_api_request("/api/analysis/vip-consumption")
    balance_analysis = make_api_request("/api/analysis/unspent-balance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if inactive_analysis:
            st.info(f"不活跃顾客: {inactive_analysis.get('description', '')}")
        
        if reopen_analysis and reopen_analysis.get('data'):
            reopen_rate = reopen_analysis['data'][0].get('reopen_rate', 0)
            st.info(f"新客二开率: {reopen_rate}%")
    
    with col2:
        if vip_analysis:
            vip_count = len(vip_analysis.get('data', []))
            st.info(f"VIP顾客: {vip_count}位")
        
        if balance_analysis:
            balance_count = len(balance_analysis.get('data', []))
            st.info(f"高余额顾客: {balance_count}位")
    
    # 图表展示
    st.subheader("📈 数据可视化")
    
    # 科室业绩分析
    dept_analysis = make_api_request("/api/analysis/department-performance")
    if dept_analysis and dept_analysis.get('data'):
        df_dept = pd.DataFrame(dept_analysis['data'])
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_dept = px.bar(
                df_dept, 
                x='department', 
                y='total_amount',
                title="科室业绩分析",
                labels={'department': '科室', 'total_amount': '总金额'}
            )
            st.plotly_chart(fig_dept, use_container_width=True)
        
        with col2:
            fig_dept_pie = px.pie(
                df_dept, 
                values='total_amount', 
                names='department',
                title="科室业绩占比"
            )
            st.plotly_chart(fig_dept_pie, use_container_width=True)
    
    # 产品表现分析
    product_analysis = make_api_request("/api/analysis/product-performance")
    if product_analysis and product_analysis.get('data'):
        df_product = pd.DataFrame(product_analysis['data'])
        
        fig_product = px.bar(
            df_product, 
            x='product_name', 
            y='total_revenue',
            color='department',
            title="产品销售额分析",
            labels={'product_name': '产品名称', 'total_revenue': '销售额', 'department': '科室'}
        )
        st.plotly_chart(fig_product, use_container_width=True)

def display_customer_management():
    """显示顾客管理页面"""
    st.header("👥 顾客管理")
    
    # 创建新顾客
    with st.expander("➕ 添加新顾客"):
        with st.form("add_customer"):
            name = st.text_input("姓名")
            phone = st.text_input("电话")
            register_date = st.date_input("注册日期", value=date.today())
            last_visit_date = st.date_input("最近到店日期", value=None)
            consultant_id = st.number_input("咨询师ID", min_value=1, value=1)
            membership_level = st.selectbox("会员等级", ["普通", "白银", "黄金", "钻石"])
            
            if st.form_submit_button("添加顾客"):
                customer_data = {
                    "name": name,
                    "phone": phone,
                    "register_date": register_date.isoformat(),
                    "last_visit_date": last_visit_date.isoformat() if last_visit_date else None,
                    "consultant_id": consultant_id,
                    "membership_level": membership_level
                }
                
                result = make_api_request("/api/customers", method="POST", data=customer_data)
                if result:
                    st.success("顾客添加成功！")
                else:
                    st.error("顾客添加失败！")
    
    # 显示顾客列表
    st.subheader("📋 顾客列表")
    customers = make_api_request("/api/customers")
    
    if customers:
        df = pd.DataFrame(customers)
        
        # 搜索功能
        search_term = st.text_input("搜索顾客姓名或电话")
        if search_term:
            df = df[df['name'].str.contains(search_term, na=False) | 
                   df['phone'].str.contains(search_term, na=False)]
        
        # 显示数据
        st.dataframe(df, use_container_width=True)
        
        # 下载功能
        csv = df.to_csv(index=False)
        st.download_button(
            label="下载顾客数据",
            data=csv,
            file_name="customers.csv",
            mime="text/csv"
        )
    else:
        st.warning("暂无顾客数据")

def display_consultant_management():
    """显示咨询师管理页面"""
    st.header("👨‍⚕️ 咨询师管理")
    
    # 创建新咨询师
    with st.expander("➕ 添加新咨询师"):
        with st.form("add_consultant"):
            name = st.text_input("姓名")
            department = st.selectbox("科室", ["皮肤科", "无创科", "整形外科"])
            
            if st.form_submit_button("添加咨询师"):
                consultant_data = {
                    "name": name,
                    "department": department
                }
                
                result = make_api_request("/api/consultants", method="POST", data=consultant_data)
                if result:
                    st.success("咨询师添加成功！")
                else:
                    st.error("咨询师添加失败！")
    
    # 显示咨询师列表
    st.subheader("📋 咨询师列表")
    consultants = make_api_request("/api/consultants")
    
    if consultants:
        df = pd.DataFrame(consultants)
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("暂无咨询师数据")

def display_product_management():
    """显示产品管理页面"""
    st.header("💊 产品管理")
    
    # 创建新产品
    with st.expander("➕ 添加新产品"):
        with st.form("add_product"):
            product_name = st.text_input("产品名称")
            department = st.selectbox("科室", ["皮肤科", "无创科", "整形外科", "综合"])
            product_type = st.selectbox("产品类型", ["流量品", "利润品", "高价款"])
            standard_price = st.number_input("标准价格", min_value=0.0, value=1000.0)
            
            if st.form_submit_button("添加产品"):
                product_data = {
                    "product_name": product_name,
                    "department": department,
                    "product_type": product_type,
                    "standard_price": float(standard_price)
                }
                
                result = make_api_request("/api/products", method="POST", data=product_data)
                if result:
                    st.success("产品添加成功！")
                else:
                    st.error("产品添加失败！")
    
    # 显示产品列表
    st.subheader("📋 产品列表")
    products = make_api_request("/api/products")
    
    if products:
        df = pd.DataFrame(products)
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("暂无产品数据")

def display_analysis():
    """显示数据分析页面"""
    st.header("📊 数据分析")
    
    # 分析选项
    analysis_options = {
        "不活跃顾客分析": "/api/analysis/inactive-customers",
        "新客二开率分析": "/api/analysis/new-customer-reopen",
        "VIP顾客消费分析": "/api/analysis/vip-consumption",
        "未划扣余额分析": "/api/analysis/unspent-balance",
        "科室业绩分析": "/api/analysis/department-performance",
        "产品表现分析": "/api/analysis/product-performance"
    }
    
    selected_analysis = st.selectbox("选择分析类型", list(analysis_options.keys()))
    
    if st.button("执行分析"):
        with st.spinner("正在分析数据..."):
            result = make_api_request(analysis_options[selected_analysis])
            
            if result:
                st.subheader(result.get('title', '分析结果'))
                st.write(result.get('description', ''))
                
                if result.get('data'):
                    df = pd.DataFrame(result['data'])
                    st.dataframe(df, use_container_width=True)
                    
                    # 生成图表
                    if len(df) > 0:
                        if 'total_amount' in df.columns:
                            fig = px.bar(df, x=df.columns[0], y='total_amount', title="分析结果")
                            st.plotly_chart(fig, use_container_width=True)
                        elif 'total_consumption' in df.columns:
                            fig = px.scatter(df, x='name', y='total_consumption', title="消费分析")
                            st.plotly_chart(fig, use_container_width=True)
                
                if result.get('summary'):
                    st.info(result['summary'])
            else:
                st.error("分析失败，请检查数据连接")

def main():
    """主函数"""
    # 侧边栏导航
    st.sidebar.title("导航菜单")
    
    page = st.sidebar.selectbox(
        "选择页面",
        ["仪表板", "顾客管理", "咨询师管理", "产品管理", "数据分析"]
    )
    
    # 页面路由
    if page == "仪表板":
        display_dashboard()
    elif page == "顾客管理":
        display_customer_management()
    elif page == "咨询师管理":
        display_consultant_management()
    elif page == "产品管理":
        display_product_management()
    elif page == "数据分析":
        display_analysis()

if __name__ == "__main__":
    main() 