#!/usr/bin/env python3
"""
医美数据管理系统 - 示例数据初始化脚本
"""

import sys
import os
from datetime import date, timedelta
import random

# 添加backend路径
sys.path.append('backend')

from models import Customer, Consultant, MedicalProduct, ConsumptionRecord, WriteOffRecord, UnspentBalance
from database import get_session

def create_sample_data():
    """创建示例数据"""
    session = get_session()
    
    print("🎯 开始创建示例数据...")
    
    # 1. 创建咨询师
    print("👨‍⚕️ 创建咨询师数据...")
    consultants = [
        Consultant(name='张美丽', department='皮肤科'),
        Consultant(name='王医生', department='无创科'),
        Consultant(name='李专家', department='整形外科'),
        Consultant(name='陈主任', department='皮肤科'),
        Consultant(name='刘教授', department='无创科')
    ]
    session.add_all(consultants)
    session.commit()
    print(f"✅ 创建了 {len(consultants)} 位咨询师")
    
    # 2. 创建产品
    print("💊 创建产品数据...")
    products = [
        MedicalProduct(product_name='玻尿酸', department='无创科', product_type='利润品', standard_price=3800),
        MedicalProduct(product_name='光子嫩肤', department='皮肤科', product_type='流量品', standard_price=1200),
        MedicalProduct(product_name='隆鼻手术', department='整形外科', product_type='高价款', standard_price=28000),
        MedicalProduct(product_name='水光针', department='皮肤科', product_type='利润品', standard_price=1800),
        MedicalProduct(product_name='肉毒素', department='无创科', product_type='利润品', standard_price=3200),
        MedicalProduct(product_name='超声刀', department='无创科', product_type='高价款', standard_price=15000),
        MedicalProduct(product_name='激光祛斑', department='皮肤科', product_type='利润品', standard_price=2500),
        MedicalProduct(product_name='双眼皮手术', department='整形外科', product_type='高价款', standard_price=12000)
    ]
    session.add_all(products)
    session.commit()
    print(f"✅ 创建了 {len(products)} 个产品")
    
    # 3. 创建客户
    print("👥 创建客户数据...")
    customers = []
    for i in range(1, 101):  # 创建100位客户
        # 随机生成注册日期（过去一年内）
        register_date = date(2023, 1, 1) + timedelta(days=random.randint(0, 365))
        
        # 随机生成最近到店日期（过去6个月内）
        last_visit_date = date(2024, 1, 1) + timedelta(days=random.randint(0, 180))
        
        # 随机选择咨询师
        consultant = random.choice(consultants)
        
        # 随机选择会员等级
        membership_level = random.choices(
            ['普通', '白银', '黄金', '钻石'],
            weights=[40, 30, 20, 10]  # 权重分布
        )[0]
        
        customer = Customer(
            name=f'客户{i:03d}',
            phone=f'1380013{8000 + i:04d}',
            register_date=register_date,
            last_visit_date=last_visit_date,
            consultant_id=consultant.consultant_id,  # 只用ID
            membership_level=membership_level,
            health_tags={
                'allergies': random.choice(['无', '花粉过敏', '药物过敏', '食物过敏']),
                'chronic_diseases': random.choice(['无', '高血压', '糖尿病', '心脏病']),
                'skin_type': random.choice(['干性', '油性', '混合性', '敏感性'])
            }
        )
        customers.append(customer)
    
    session.add_all(customers)
    session.commit()
    # 重新查询，避免游离对象
    customers = session.query(Customer).all()
    print(f"✅ 创建了 {len(customers)} 位客户")
    
    # 4. 创建消费记录
    print("💰 创建消费记录...")
    consumption_records = []
    for customer in customers:
        # 每位客户随机生成1-8条消费记录
        num_records = random.randint(1, 8)
        
        for _ in range(num_records):
            product = random.choice(products)
            
            # 随机生成消费日期（在注册日期之后，最近到店日期之前）
            consume_date = customer.register_date + timedelta(
                days=random.randint(0, (customer.last_visit_date - customer.register_date).days)
            )
            
            # 随机生成消费金额（标准价格的80%-120%）
            amount = float(product.standard_price) * random.uniform(0.8, 1.2)
            
            # 新客标识（第一次消费为新客）
            is_new_customer = _ == 0
            
            record = ConsumptionRecord(
                customer_id=customer.customer_id,
                consume_date=consume_date,
                amount=amount,
                department=product.department,
                is_new_customer=is_new_customer,
                consultant_id=customer.consultant_id,
                product_id=product.product_id,
                quantity=random.randint(1, 3),
                payment_method=random.choice(['现金', '银行卡', '分期', '医保']),
                related_campaign=random.choice([None, '春节活动', '会员专享', '新客优惠', '周年庆'])
            )
            consumption_records.append(record)
    
    session.add_all(consumption_records)
    session.commit()
    print(f"✅ 创建了 {len(consumption_records)} 条消费记录")
    
    # 5. 创建划扣记录和未划扣余额
    print("💳 创建划扣记录和余额...")
    write_off_records = []
    unspent_balances = []
    
    for record in consumption_records:
        # 70%概率有划扣记录
        if random.random() > 0.3:
            # 划扣金额为消费金额的50%-100%
            write_off_amount = float(record.amount) * random.uniform(0.5, 1.0)
            
            # 划扣日期在消费日期之后1-30天
            write_off_date = record.consume_date + timedelta(days=random.randint(1, 30))
            
            write_off = WriteOffRecord(
                customer_id=record.customer_id,
                write_off_date=write_off_date,
                amount=write_off_amount,
                department=record.department,
                product_id=record.product_id,
                quantity=record.quantity,
                consultant_id=record.consultant_id,
                consume_record_id=record.record_id,
                write_off_type=random.choice(['正常划扣', '活动核销', '套餐消耗'])
            )
            write_off_records.append(write_off)
        
        # 创建未划扣余额记录
        balance = UnspentBalance(
            customer_id=record.customer_id,
            product_id=record.product_id,
            total_amount=record.amount,
            spent_amount=0,  # 初始为0，后续会更新
            expiration_date=record.consume_date + timedelta(days=365)
        )
        unspent_balances.append(balance)
    
    session.add_all(write_off_records)
    session.add_all(unspent_balances)
    session.commit()
    print(f"✅ 创建了 {len(write_off_records)} 条划扣记录")
    print(f"✅ 创建了 {len(unspent_balances)} 条余额记录")
    
    # 6. 更新余额记录
    print("🔄 更新余额记录...")
    for write_off in write_off_records:
        # 找到对应的余额记录并更新
        balance = session.query(UnspentBalance).filter(
            UnspentBalance.customer_id == write_off.customer_id,
            UnspentBalance.product_id == write_off.product_id
        ).first()
        
        if balance:
            balance.spent_amount += write_off.amount
            balance.last_write_off_date = write_off.write_off_date
    
    session.commit()
    print("✅ 余额记录更新完成")
    
    session.close()
    
    # 7. 生成统计报告
    print("\n📊 数据统计报告:")
    print(f"   👨‍⚕️ 咨询师: {len(consultants)} 位")
    print(f"   💊 产品: {len(products)} 个")
    print(f"   👥 客户: {len(customers)} 位")
    print(f"   💰 消费记录: {len(consumption_records)} 条")
    print(f"   💳 划扣记录: {len(write_off_records)} 条")
    print(f"   💎 余额记录: {len(unspent_balances)} 条")
    
    # 会员等级分布
    membership_counts = {}
    for customer in customers:
        membership_counts[customer.membership_level] = membership_counts.get(customer.membership_level, 0) + 1
    
    print("\n👑 会员等级分布:")
    for level, count in membership_counts.items():
        print(f"   {level}: {count} 位")
    
    # 科室分布
    dept_counts = {}
    for consultant in consultants:
        dept_counts[consultant.department] = dept_counts.get(consultant.department, 0) + 1
    
    print("\n🏥 科室分布:")
    for dept, count in dept_counts.items():
        print(f"   {dept}: {count} 位咨询师")
    
    print("\n🎉 示例数据创建完成！")
    print("💡 现在可以启动系统并查看数据了")

if __name__ == "__main__":
    try:
        create_sample_data()
    except Exception as e:
        print(f"❌ 创建示例数据失败: {e}")
        print("请确保:")
        print("1. 数据库连接正常")
        print("2. 环境变量配置正确")
        print("3. 依赖包已安装") 