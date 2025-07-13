import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="十大增长点分析", page_icon="📈")

st.title("📈 十大增长点分析")

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

# 增长点分析函数
def analyze_growth_opportunities():
    """分析十大增长机会"""
    opportunities = []
    
    # 1. 不活跃客户召回
    inactive_analysis = make_api_request("/api/analysis/inactive-customers")
    if inactive_analysis and inactive_analysis.get('data'):
        inactive_count = len(inactive_analysis['data'])
        opportunities.append({
            'category': '客户召回',
            'opportunity': '不活跃客户召回',
            'description': f'有{inactive_count}位客户6个月以上未到店',
            'potential_value': inactive_count * 2000,  # 假设每位客户平均消费2000元
            'priority': '高',
            'action': '制定客户回访计划，提供专属优惠'
        })
    
    # 2. VIP客户深度开发
    vip_analysis = make_api_request("/api/analysis/vip-consumption")
    if vip_analysis and vip_analysis.get('data'):
        vip_customers = vip_analysis['data']
        high_value_vips = [c for c in vip_customers if c.get('total_consumption', 0) > 10000]
        opportunities.append({
            'category': 'VIP开发',
            'opportunity': '高价值VIP客户深度开发',
            'description': f'有{len(high_value_vips)}位VIP客户消费超过1万元',
            'potential_value': len(high_value_vips) * 5000,
            'priority': '高',
            'action': '提供个性化服务，推荐高端项目'
        })
    
    # 3. 新客转化率提升
    reopen_analysis = make_api_request("/api/analysis/new-customer-reopen")
    if reopen_analysis and reopen_analysis.get('data'):
        reopen_rate = reopen_analysis['data'][0].get('reopen_rate', 0)
        if reopen_rate < 50:  # 如果二开率低于50%
            opportunities.append({
                'category': '新客转化',
                'opportunity': '提升新客二开率',
                'description': f'当前新客二开率为{reopen_rate}%，有较大提升空间',
                'potential_value': 50000,  # 假设提升10%可带来5万元收入
                'priority': '中',
                'action': '优化新客体验，制定二次消费激励政策'
            })
    
    # 4. 未划扣余额激活
    balance_analysis = make_api_request("/api/analysis/unspent-balance")
    if balance_analysis and balance_analysis.get('data'):
        total_balance = sum([b.get('remaining_amount', 0) for b in balance_analysis['data']])
        opportunities.append({
            'category': '余额激活',
            'opportunity': '激活未划扣余额',
            'description': f'有{len(balance_analysis["data"])}位客户未划扣余额总计{total_balance:.0f}元',
            'potential_value': total_balance * 0.3,  # 假设30%的余额会被使用
            'priority': '高',
            'action': '主动联系客户，推荐相关项目'
        })
    
    # 5. 科室业绩优化
    dept_analysis = make_api_request("/api/analysis/department-performance")
    if dept_analysis and dept_analysis.get('data'):
        dept_data = dept_analysis['data']
        # 找出业绩最低的科室
        min_dept = min(dept_data, key=lambda x: x.get('total_amount', 0))
        opportunities.append({
            'category': '科室优化',
            'opportunity': f'{min_dept["department"]}科室业绩提升',
            'description': f'{min_dept["department"]}科室业绩较低，有提升空间',
            'potential_value': 30000,
            'priority': '中',
            'action': '加强科室推广，培训咨询师技能'
        })
    
    # 6. 产品组合销售
    product_analysis = make_api_request("/api/analysis/product-performance")
    if product_analysis and product_analysis.get('data'):
        products = product_analysis['data']
        # 找出销售最好的产品
        best_product = max(products, key=lambda x: x.get('total_revenue', 0))
        opportunities.append({
            'category': '产品策略',
            'opportunity': f'{best_product["product_name"]}产品组合销售',
            'description': f'{best_product["product_name"]}销售表现优秀，可开发相关产品',
            'potential_value': 40000,
            'priority': '中',
            'action': '开发配套产品，制定组合销售方案'
        })
    
    # 7. 会员等级升级
    customers = make_api_request("/api/customers")
    if customers:
        silver_customers = [c for c in customers if c.get('membership_level') == '白银']
        opportunities.append({
            'category': '会员升级',
            'opportunity': '白银会员升级计划',
            'description': f'有{len(silver_customers)}位白银会员可升级为黄金会员',
            'potential_value': len(silver_customers) * 3000,
            'priority': '中',
            'action': '制定会员升级激励政策'
        })
    
    # 8. 季节性营销
    opportunities.append({
        'category': '营销策略',
        'opportunity': '季节性营销活动',
        'description': '根据医美行业特点，制定季节性营销计划',
        'potential_value': 100000,
        'priority': '中',
        'action': '策划节假日和季节性营销活动'
    })
    
    # 9. 客户推荐计划
    opportunities.append({
        'category': '客户推荐',
        'opportunity': '客户推荐奖励计划',
        'description': '通过现有客户推荐新客户',
        'potential_value': 80000,
        'priority': '低',
        'action': '制定客户推荐奖励机制'
    })
    
    # 10. 数字化营销
    opportunities.append({
        'category': '数字化',
        'opportunity': '数字化营销渠道拓展',
        'description': '利用社交媒体和线上平台拓展客户',
        'potential_value': 60000,
        'priority': '低',
        'action': '建立线上营销体系，提升品牌知名度'
    })
    
    return opportunities

# 主界面
st.markdown("""
### 分析说明
本页面分析医美机构的十大增长机会，基于现有数据提供具体的改进建议和潜在价值评估。
""")

# 执行分析
if st.button("🚀 开始分析", type="primary"):
    with st.spinner("正在分析增长机会..."):
        opportunities = analyze_growth_opportunities()
        
        if opportunities:
            st.success(f"分析完成！发现 {len(opportunities)} 个增长机会")
            
            # 创建DataFrame
            df = pd.DataFrame(opportunities)
            
            # 按优先级排序
            priority_order = {'高': 1, '中': 2, '低': 3}
            df['priority_order'] = df['priority'].map(priority_order)
            df = df.sort_values(['priority_order', 'potential_value'], ascending=[True, False])
            df = df.drop('priority_order', axis=1)
            
            # 显示总体统计
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("总增长机会", len(opportunities))
            with col2:
                total_potential = df['potential_value'].sum()
                st.metric("总潜在价值", f"¥{total_potential:,.0f}")
            with col3:
                high_priority = len(df[df['priority'] == '高'])
                st.metric("高优先级机会", high_priority)
            
            # 显示详细结果
            st.subheader("📊 增长机会详情")
            
            # 按类别分组显示
            categories = df['category'].unique()
            for category in categories:
                category_data = df[df['category'] == category]
                
                with st.expander(f"📁 {category} ({len(category_data)}个机会)"):
                    for _, row in category_data.iterrows():
                        st.markdown(f"""
                        **{row['opportunity']}** ({row['priority']}优先级)
                        - 描述: {row['description']}
                        - 潜在价值: ¥{row['potential_value']:,.0f}
                        - 建议行动: {row['action']}
                        """)
                        st.divider()
            
            # 可视化分析
            st.subheader("📈 可视化分析")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # 按类别统计
                fig_category = px.bar(
                    df.groupby('category')['potential_value'].sum().reset_index(),
                    x='category',
                    y='potential_value',
                    title="各类别潜在价值",
                    labels={'potential_value': '潜在价值 (元)', 'category': '类别'}
                )
                st.plotly_chart(fig_category, use_container_width=True)
            
            with col2:
                # 按优先级统计
                fig_priority = px.pie(
                    df.groupby('priority')['potential_value'].sum().reset_index(),
                    values='potential_value',
                    names='priority',
                    title="按优先级分布"
                )
                st.plotly_chart(fig_priority, use_container_width=True)
            
            # 详细表格
            st.subheader("📋 详细数据")
            st.dataframe(df, use_container_width=True)
            
            # 下载功能
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 下载分析报告",
                data=csv,
                file_name=f"growth_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
            
            # 行动建议
            st.subheader("💡 行动建议")
            
            high_priority_ops = df[df['priority'] == '高']
            if not high_priority_ops.empty:
                st.info("**高优先级行动建议：**")
                for _, op in high_priority_ops.iterrows():
                    st.markdown(f"- **{op['opportunity']}**: {op['action']}")
            
            st.success("**下一步行动：**")
            st.markdown("""
            1. 优先执行高优先级增长机会
            2. 制定具体的执行计划和时间表
            3. 分配资源和责任人
            4. 建立跟踪和评估机制
            5. 定期回顾和调整策略
            """)
        else:
            st.warning("无法获取数据进行分析，请确保后端服务正常运行")

# 分析说明
with st.expander("📚 分析说明"):
    st.markdown("""
    **增长机会评估标准：**
    
    1. **客户召回**: 基于不活跃客户数量和潜在消费能力
    2. **VIP开发**: 基于高价值客户的深度开发潜力
    3. **新客转化**: 基于新客二开率和转化提升空间
    4. **余额激活**: 基于未划扣余额的激活潜力
    5. **科室优化**: 基于各科室业绩表现和提升空间
    6. **产品策略**: 基于产品销售表现和组合机会
    7. **会员升级**: 基于会员等级升级的潜在价值
    8. **营销策略**: 基于季节性营销的机会
    9. **客户推荐**: 基于推荐营销的潜力
    10. **数字化**: 基于线上营销的发展机会
    
    **优先级评估：**
    - 高优先级: 直接影响收入，执行难度较低
    - 中优先级: 有较大潜力，需要一定投入
    - 低优先级: 长期价值，需要持续投入
    """) 