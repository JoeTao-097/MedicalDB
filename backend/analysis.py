from database import get_session
from models import Customer, Consultant, MedicalProduct, ConsumptionRecord, WriteOffRecord, UnspentBalance
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy import func

def analyze_inactive_customers(months=6):
    """分析指定月数以上不活跃顾客"""
    session = get_session()
    cutoff_date = datetime.now() - timedelta(days=months*30)
    
    inactive_customers = session.query(Customer).filter(
        Customer.last_visit_date < cutoff_date
    ).all()
    
    results = []
    for cust in inactive_customers:
        results.append({
            'customer_id': cust.customer_id,
            'name': cust.name,
            'phone': cust.phone,
            'last_visit_date': cust.last_visit_date,
            'membership_level': cust.membership_level,
            'total_consumption': float(cust.total_consumption) if cust.total_consumption else 0
        })
    
    session.close()
    return {
        'title': f'{months}个月以上不活跃顾客分析',
        'description': f'找到 {len(results)} 位{months}个月以上不活跃顾客',
        'data': results,
        'summary': f'共有{len(results)}位顾客{months}个月以上未到店，建议进行客户回访'
    }

def analyze_new_customer_reopen():
    """分析新客二开率"""
    session = get_session()
    
    # 获取所有新客
    new_customers = session.query(ConsumptionRecord.customer_id).filter(
        ConsumptionRecord.is_new_customer == True
    ).distinct().subquery()
    
    # 获取二开顾客
    reopened_customers = session.query(ConsumptionRecord.customer_id).filter(
        ConsumptionRecord.customer_id.in_(new_customers),
        ConsumptionRecord.is_new_customer == False
    ).distinct().subquery()
    
    # 计算二开率
    total_new = session.query(new_customers).count()
    total_reopened = session.query(reopened_customers).count()
    reopen_rate = (total_reopened / total_new) * 100 if total_new > 0 else 0
    
    session.close()
    return {
        'title': '新客二开率分析',
        'description': f'新客总数: {total_new}, 二次消费顾客数: {total_reopened}',
        'data': [{
            'total_new': total_new,
            'total_reopened': total_reopened,
            'reopen_rate': round(reopen_rate, 2)
        }],
        'summary': f'新客二开率为{reopen_rate:.2f}%，建议优化新客转化策略'
    }

def analyze_vip_consumption():
    """分析VIP客群消费情况"""
    session = get_session()
    
    vip_customers = session.query(Customer).filter(
        Customer.membership_level.in_(['黄金', '钻石'])
    )
    
    results = []
    for cust in vip_customers:
        total = sum([c.amount for c in cust.consumptions])
        last_visit_days = (datetime.now().date() - cust.last_visit_date).days if cust.last_visit_date else None
        results.append({
            'customer_id': cust.customer_id,
            'name': cust.name,
            'membership': cust.membership_level,
            'total_consumption': float(total),
            'last_visit_days': last_visit_days,
            'phone': cust.phone
        })
    
    # 按最近到店时间排序
    results.sort(key=lambda x: x['last_visit_days'] if x['last_visit_days'] else 0, reverse=True)
    
    session.close()
    return {
        'title': 'VIP顾客消费分析',
        'description': f'共有{len(results)}位VIP顾客',
        'data': results,
        'summary': f'VIP顾客平均消费{sum(r["total_consumption"] for r in results)/len(results):.2f}元'
    }

def analyze_unspent_balance():
    """分析未划扣余额"""
    session = get_session()
    
    high_balance = session.query(
        Customer.name,
        MedicalProduct.product_name,
        UnspentBalance.remaining_amount
    ).join(UnspentBalance, UnspentBalance.customer_id == Customer.customer_id
    ).join(MedicalProduct, MedicalProduct.product_id == UnspentBalance.product_id
    ).filter(
        UnspentBalance.remaining_amount > 5000
    ).order_by(UnspentBalance.remaining_amount.desc()).all()
    
    results = []
    for row in high_balance:
        results.append({
            'customer_name': row.name,
            'product_name': row.product_name,
            'remaining_amount': float(row.remaining_amount)
        })
    
    session.close()
    return {
        'title': '高未划扣余额分析',
        'description': f'未划扣余额超过5000元的客户共{len(results)}位',
        'data': results,
        'summary': f'总未划扣余额{sum(r["remaining_amount"] for r in results):.2f}元'
    }

def analyze_department_performance():
    """分析科室业绩表现"""
    session = get_session()
    
    # 按科室统计消费金额
    dept_stats = session.query(
        ConsumptionRecord.department,
        func.count(ConsumptionRecord.record_id).label('total_records'),
        func.sum(ConsumptionRecord.amount).label('total_amount')
    ).group_by(ConsumptionRecord.department).all()
    
    results = []
    for dept in dept_stats:
        results.append({
            'department': dept.department,
            'total_records': dept.total_records,
            'total_amount': float(dept.total_amount) if dept.total_amount else 0
        })
    
    session.close()
    return {
        'title': '科室业绩分析',
        'description': '各科室消费情况统计',
        'data': results,
        'summary': f'总消费金额{sum(r["total_amount"] for r in results):.2f}元'
    }

def analyze_product_performance():
    """分析产品表现"""
    session = get_session()
    
    # 按产品统计消费情况
    product_stats = session.query(
        MedicalProduct.product_name,
        MedicalProduct.department,
        MedicalProduct.product_type,
        func.count(ConsumptionRecord.record_id).label('total_sales'),
        func.sum(ConsumptionRecord.amount).label('total_revenue')
    ).join(ConsumptionRecord, MedicalProduct.product_id == ConsumptionRecord.product_id
    ).group_by(MedicalProduct.product_id).all()
    
    results = []
    for product in product_stats:
        results.append({
            'product_name': product.product_name,
            'department': product.department,
            'product_type': product.product_type,
            'total_sales': product.total_sales,
            'total_revenue': float(product.total_revenue) if product.total_revenue else 0
        })
    
    session.close()
    return {
        'title': '产品表现分析',
        'description': '各产品销售情况统计',
        'data': results,
        'summary': f'总销售额{sum(r["total_revenue"] for r in results):.2f}元'
    } 