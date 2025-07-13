import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
import json

st.set_page_config(page_title="数据管理", page_icon="🗄️")

st.title("🗄️ 数据管理")

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
        elif method == "PUT":
            response = requests.put(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API请求错误: {str(e)}")
        return None

# 侧边栏导航
st.sidebar.title("数据管理")
management_type = st.sidebar.selectbox(
    "选择管理类型",
    ["顾客管理", "咨询师管理", "产品管理", "消费记录管理", "划扣记录管理", "余额管理"]
)

if management_type == "顾客管理":
    st.header("👥 顾客管理")
    
    # 创建新顾客
    with st.expander("➕ 添加新顾客", expanded=True):
        with st.form("add_customer_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("姓名 *", placeholder="请输入顾客姓名")
                phone = st.text_input("电话 *", placeholder="请输入联系电话")
                register_date = st.date_input("注册日期 *", value=date.today())
                last_visit_date = st.date_input("最近到店日期", value=None)
            
            with col2:
                consultant_id = st.number_input("咨询师ID *", min_value=1, value=1)
                membership_level = st.selectbox("会员等级", ["普通", "白银", "黄金", "钻石"], index=0)
                health_tags = st.text_area("健康标签", placeholder="过敏史、慢性病等，JSON格式")
            
            if st.form_submit_button("添加顾客"):
                if name and phone:
                    customer_data = {
                        "name": name,
                        "phone": phone,
                        "register_date": register_date.isoformat(),
                        "last_visit_date": last_visit_date.isoformat() if last_visit_date else None,
                        "consultant_id": consultant_id,
                        "membership_level": membership_level,
                        "health_tags": json.loads(health_tags) if health_tags else None
                    }
                    
                    result = make_api_request("/api/customers", method="POST", data=customer_data)
                    if result:
                        st.success("顾客添加成功！")
                        st.rerun()
                    else:
                        st.error("顾客添加失败！")
                else:
                    st.error("请填写必填字段！")
    
    # 顾客列表
    st.subheader("📋 顾客列表")
    customers = make_api_request("/api/customers")
    
    if customers:
        df = pd.DataFrame(customers)
        
        # 搜索和筛选
        col1, col2 = st.columns(2)
        with col1:
            search_term = st.text_input("搜索顾客姓名或电话")
        with col2:
            membership_filter = st.selectbox("会员等级筛选", ["全部"] + list(df['membership_level'].unique()))
        
        # 应用筛选
        if search_term:
            df = df[df['name'].str.contains(search_term, na=False) | 
                   df['phone'].str.contains(search_term, na=False)]
        
        if membership_filter != "全部":
            df = df[df['membership_level'] == membership_filter]
        
        # 显示数据
        st.dataframe(df, use_container_width=True)
        
        # 统计信息
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("总顾客数", len(df))
        with col2:
            st.metric("VIP顾客", len(df[df['membership_level'].isin(['黄金', '钻石'])]))
        with col3:
            st.metric("新顾客", len(df[df['membership_level'] == '普通']))
        with col4:
            if 'total_consumption' in df.columns:
                # 确保数值字段为数字类型
                df['total_consumption'] = pd.to_numeric(df['total_consumption'], errors='coerce')
                avg_consumption = df['total_consumption'].mean()
            else:
                avg_consumption = 0
            st.metric("平均消费", f"¥{avg_consumption:.0f}")
        
        # 下载功能
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 下载顾客数据",
            data=csv,
            file_name=f"customers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.warning("暂无顾客数据")

elif management_type == "咨询师管理":
    st.header("👨‍⚕️ 咨询师管理")
    
    # 创建新咨询师
    with st.expander("➕ 添加新咨询师", expanded=True):
        with st.form("add_consultant_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("姓名 *", placeholder="请输入咨询师姓名")
            
            with col2:
                department = st.selectbox("科室 *", ["皮肤科", "无创科", "整形外科"])
            
            if st.form_submit_button("添加咨询师"):
                if name:
                    consultant_data = {
                        "name": name,
                        "department": department
                    }
                    
                    result = make_api_request("/api/consultants", method="POST", data=consultant_data)
                    if result:
                        st.success("咨询师添加成功！")
                        st.rerun()
                    else:
                        st.error("咨询师添加失败！")
                else:
                    st.error("请填写必填字段！")
    
    # 咨询师列表
    st.subheader("📋 咨询师列表")
    consultants = make_api_request("/api/consultants")
    
    if consultants:
        df = pd.DataFrame(consultants)
        
        # 按科室筛选
        department_filter = st.selectbox("科室筛选", ["全部"] + list(df['department'].unique()))
        
        if department_filter != "全部":
            df = df[df['department'] == department_filter]
        
        st.dataframe(df, use_container_width=True)
        
        # 统计信息
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("总咨询师数", len(df))
        with col2:
            st.metric("皮肤科", len(df[df['department'] == '皮肤科']))
        with col3:
            st.metric("无创科", len(df[df['department'] == '无创科']))
        
        # 下载功能
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 下载咨询师数据",
            data=csv,
            file_name=f"consultants_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.warning("暂无咨询师数据")

elif management_type == "产品管理":
    st.header("💊 产品管理")
    
    # 创建新产品
    with st.expander("➕ 添加新产品", expanded=True):
        with st.form("add_product_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                product_name = st.text_input("产品名称 *", placeholder="请输入产品名称")
                department = st.selectbox("科室 *", ["皮肤科", "无创科", "整形外科", "综合"])
            
            with col2:
                product_type = st.selectbox("产品类型 *", ["流量品", "利润品", "高价款"])
                standard_price = st.number_input("标准价格 *", min_value=0.0, value=1000.0, step=100.0)
            
            if st.form_submit_button("添加产品"):
                if product_name and standard_price > 0:
                    product_data = {
                        "product_name": product_name,
                        "department": department,
                        "product_type": product_type,
                        "standard_price": float(standard_price)
                    }
                    
                    result = make_api_request("/api/products", method="POST", data=product_data)
                    if result:
                        st.success("产品添加成功！")
                        st.rerun()
                    else:
                        st.error("产品添加失败！")
                else:
                    st.error("请填写必填字段！")
    
    # 产品列表
    st.subheader("📋 产品列表")
    products = make_api_request("/api/products")
    
    if products:
        df = pd.DataFrame(products)
        
        # 筛选
        col1, col2 = st.columns(2)
        with col1:
            department_filter = st.selectbox("科室筛选", ["全部"] + list(df['department'].unique()))
        with col2:
            type_filter = st.selectbox("类型筛选", ["全部"] + list(df['product_type'].unique()))
        
        # 应用筛选
        if department_filter != "全部":
            df = df[df['department'] == department_filter]
        if type_filter != "全部":
            df = df[df['product_type'] == type_filter]
        
        st.dataframe(df, use_container_width=True)
        
        # 统计信息
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("总产品数", len(df))
        with col2:
            st.metric("流量品", len(df[df['product_type'] == '流量品']))
        with col3:
            st.metric("利润品", len(df[df['product_type'] == '利润品']))
        with col4:
            # 确保数值字段为数字类型
            df['standard_price'] = pd.to_numeric(df['standard_price'], errors='coerce')
            avg_price = df['standard_price'].mean()
            st.metric("平均价格", f"¥{avg_price:.0f}")
        
        # 下载功能
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 下载产品数据",
            data=csv,
            file_name=f"products_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.warning("暂无产品数据")

elif management_type == "消费记录管理":
    st.header("💰 消费记录管理")
    
    # 创建新消费记录
    with st.expander("➕ 添加新消费记录", expanded=True):
        with st.form("add_consumption_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                customer_id = st.number_input("顾客ID *", min_value=1, value=1)
                consume_date = st.date_input("消费日期 *", value=date.today())
                amount = st.number_input("消费金额 *", min_value=0.0, value=1000.0, step=100.0)
                department = st.selectbox("科室 *", ["皮肤科", "无创科", "整形外科", "综合"])
            
            with col2:
                is_new_customer = st.checkbox("新客标识")
                consultant_id = st.number_input("咨询师ID *", min_value=1, value=1)
                product_id = st.number_input("产品ID *", min_value=1, value=1)
                quantity = st.number_input("购买数量", min_value=1, value=1)
                payment_method = st.selectbox("支付方式", ["现金", "银行卡", "分期", "医保"])
            
            related_campaign = st.text_input("关联营销活动", placeholder="可选")
            
            if st.form_submit_button("添加消费记录"):
                if customer_id and amount > 0:
                    consumption_data = {
                        "customer_id": customer_id,
                        "consume_date": consume_date.isoformat(),
                        "amount": float(amount),
                        "department": department,
                        "is_new_customer": is_new_customer,
                        "consultant_id": consultant_id,
                        "product_id": product_id,
                        "quantity": quantity,
                        "payment_method": payment_method,
                        "related_campaign": related_campaign if related_campaign else None
                    }
                    
                    result = make_api_request("/api/consumption-records", method="POST", data=consumption_data)
                    if result:
                        st.success("消费记录添加成功！")
                        st.rerun()
                    else:
                        st.error("消费记录添加失败！")
                else:
                    st.error("请填写必填字段！")
    
    # 消费记录列表
    st.subheader("📋 消费记录列表")
    consumption_records = make_api_request("/api/consumption-records")
    
    if consumption_records:
        df = pd.DataFrame(consumption_records)
        
        # 筛选
        col1, col2, col3 = st.columns(3)
        with col1:
            department_filter = st.selectbox("科室筛选", ["全部"] + list(df['department'].unique()))
        with col2:
            payment_filter = st.selectbox("支付方式筛选", ["全部"] + list(df['payment_method'].unique()))
        with col3:
            new_customer_filter = st.selectbox("新客筛选", ["全部", "新客", "老客"])
        
        # 应用筛选
        if department_filter != "全部":
            df = df[df['department'] == department_filter]
        if payment_filter != "全部":
            df = df[df['payment_method'] == payment_filter]
        if new_customer_filter == "新客":
            df = df[df['is_new_customer'] == True]
        elif new_customer_filter == "老客":
            df = df[df['is_new_customer'] == False]
        
        st.dataframe(df, use_container_width=True)
        
        # 统计信息
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("总记录数", len(df))
        with col2:
            # 确保数值字段为数字类型
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
            total_amount = df['amount'].sum()
            st.metric("总金额", f"¥{total_amount:.0f}")
        with col3:
            avg_amount = df['amount'].mean()
            st.metric("平均金额", f"¥{avg_amount:.0f}")
        with col4:
            new_customer_count = len(df[df['is_new_customer'] == True])
            st.metric("新客数", new_customer_count)
        
        # 下载功能
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 下载消费记录",
            data=csv,
            file_name=f"consumption_records_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.warning("暂无消费记录数据")

elif management_type == "划扣记录管理":
    st.header("💳 划扣记录管理")
    
    # 创建新划扣记录
    with st.expander("➕ 添加新划扣记录", expanded=True):
        with st.form("add_writeoff_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                customer_id = st.number_input("顾客ID *", min_value=1, value=1)
                write_off_date = st.date_input("划扣日期 *", value=date.today())
                amount = st.number_input("划扣金额 *", min_value=0.0, value=500.0, step=50.0)
                department = st.selectbox("科室 *", ["皮肤科", "无创科", "整形外科", "综合"])
            
            with col2:
                product_id = st.number_input("产品ID *", min_value=1, value=1)
                quantity = st.number_input("划扣数量", min_value=1, value=1)
                consultant_id = st.number_input("咨询师ID *", min_value=1, value=1)
                consume_record_id = st.number_input("关联消费记录ID *", min_value=1, value=1)
                write_off_type = st.selectbox("划扣类型", ["正常划扣", "活动核销", "套餐消耗"])
            
            if st.form_submit_button("添加划扣记录"):
                if customer_id and amount > 0:
                    writeoff_data = {
                        "customer_id": customer_id,
                        "write_off_date": write_off_date.isoformat(),
                        "amount": float(amount),
                        "department": department,
                        "product_id": product_id,
                        "quantity": quantity,
                        "consultant_id": consultant_id,
                        "consume_record_id": consume_record_id,
                        "write_off_type": write_off_type
                    }
                    
                    result = make_api_request("/api/write-off-records", method="POST", data=writeoff_data)
                    if result:
                        st.success("划扣记录添加成功！")
                        st.rerun()
                    else:
                        st.error("划扣记录添加失败！")
                else:
                    st.error("请填写必填字段！")
    
    # 划扣记录列表
    st.subheader("📋 划扣记录列表")
    write_off_records = make_api_request("/api/write-off-records")
    
    if write_off_records:
        df = pd.DataFrame(write_off_records)
        
        # 筛选
        col1, col2 = st.columns(2)
        with col1:
            department_filter = st.selectbox("科室筛选", ["全部"] + list(df['department'].unique()))
        with col2:
            type_filter = st.selectbox("划扣类型筛选", ["全部"] + list(df['write_off_type'].unique()))
        
        # 应用筛选
        if department_filter != "全部":
            df = df[df['department'] == department_filter]
        if type_filter != "全部":
            df = df[df['write_off_type'] == type_filter]
        
        st.dataframe(df, use_container_width=True)
        
        # 统计信息
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("总划扣记录", len(df))
        with col2:
            # 确保数值字段为数字类型
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
            total_amount = df['amount'].sum()
            st.metric("总划扣金额", f"¥{total_amount:.0f}")
        with col3:
            avg_amount = df['amount'].mean()
            st.metric("平均划扣金额", f"¥{avg_amount:.0f}")
        
        # 下载功能
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 下载划扣记录",
            data=csv,
            file_name=f"write_off_records_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.warning("暂无划扣记录数据")

elif management_type == "余额管理":
    st.header("💎 余额管理")
    
    # 创建新余额记录
    with st.expander("➕ 添加新余额记录", expanded=True):
        with st.form("add_balance_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                customer_id = st.number_input("顾客ID *", min_value=1, value=1)
                product_id = st.number_input("产品ID *", min_value=1, value=1)
                total_amount = st.number_input("总购买金额 *", min_value=0.0, value=1000.0, step=100.0)
                spent_amount = st.number_input("已划扣金额", min_value=0.0, value=0.0, step=100.0)
            
            with col2:
                last_write_off_date = st.date_input("最后划扣日期", value=None)
                expiration_date = st.date_input("有效期至", value=date.today() + timedelta(days=365))
            
            if st.form_submit_button("添加余额记录"):
                if customer_id and total_amount > 0:
                    balance_data = {
                        "customer_id": customer_id,
                        "product_id": product_id,
                        "total_amount": float(total_amount),
                        "spent_amount": float(spent_amount),
                        "last_write_off_date": last_write_off_date.isoformat() if last_write_off_date else None,
                        "expiration_date": expiration_date.isoformat() if expiration_date else None
                    }
                    
                    result = make_api_request("/api/unspent-balances", method="POST", data=balance_data)
                    if result:
                        st.success("余额记录添加成功！")
                        st.rerun()
                    else:
                        st.error("余额记录添加失败！")
                else:
                    st.error("请填写必填字段！")
    
    # 余额列表
    st.subheader("📋 余额列表")
    unspent_balances = make_api_request("/api/unspent-balances")
    
    if unspent_balances:
        df = pd.DataFrame(unspent_balances)
        
        # 计算剩余金额
        if 'total_amount' in df.columns and 'spent_amount' in df.columns:
            # 确保数值字段为数字类型
            df['total_amount'] = pd.to_numeric(df['total_amount'], errors='coerce')
            df['spent_amount'] = pd.to_numeric(df['spent_amount'], errors='coerce')
            df['remaining_amount'] = df['total_amount'] - df['spent_amount']
        
        st.dataframe(df, use_container_width=True)
        
        # 统计信息
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("总余额记录", len(df))
        with col2:
            total_balance = df['total_amount'].sum() if 'total_amount' in df.columns else 0
            st.metric("总购买金额", f"¥{total_balance:.0f}")
        with col3:
            total_spent = df['spent_amount'].sum() if 'spent_amount' in df.columns else 0
            st.metric("总已划扣", f"¥{total_spent:.0f}")
        with col4:
            total_remaining = df['remaining_amount'].sum() if 'remaining_amount' in df.columns else 0
            st.metric("总剩余金额", f"¥{total_remaining:.0f}")
        
        # 高余额提醒
        if 'remaining_amount' in df.columns:
            high_balance = df[df['remaining_amount'] > 5000]
            if not high_balance.empty:
                st.warning(f"⚠️ 有 {len(high_balance)} 位客户余额超过5000元，建议主动联系")
        
        # 下载功能
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 下载余额数据",
            data=csv,
            file_name=f"unspent_balances_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.warning("暂无余额数据")

# 数据导入导出功能
st.sidebar.divider()
st.sidebar.subheader("📤 数据导入导出")

if st.sidebar.button("🔄 刷新所有数据"):
    st.rerun()

# 系统状态
st.sidebar.divider()
st.sidebar.subheader("🔧 系统状态")

# 检查API连接
api_status = make_api_request("/")
if api_status:
    st.sidebar.success("✅ API连接正常")
else:
    st.sidebar.error("❌ API连接失败") 