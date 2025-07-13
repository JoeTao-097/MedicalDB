from sqlalchemy import create_engine, Column, Integer, String, Date, Float, Enum, Boolean, ForeignKey, JSON, text
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.ext.hybrid import hybrid_property
from database import get_engine

Base = declarative_base()

class Customer(Base):
    __tablename__ = 'customers'
    
    customer_id = Column(Integer, primary_key=True, autoincrement=True, comment='顾客编号')
    name = Column(String(100), nullable=False, comment='顾客姓名')
    phone = Column(String(20), unique=True, comment='联系电话')
    register_date = Column(Date, nullable=False, comment='注册日期')
    last_visit_date = Column(Date, comment='最近到店日期')
    consultant_id = Column(Integer, ForeignKey('consultants.consultant_id'), nullable=False, comment='专属咨询师')
    health_tags = Column(JSON, comment='健康标签(过敏史/慢性病等)')
    membership_level = Column(Enum('普通', '白银', '黄金', '钻石'), default='普通', comment='会员等级')
    
    # 关系定义
    consumptions = relationship("ConsumptionRecord", back_populates="customer")
    write_offs = relationship("WriteOffRecord", back_populates="customer")
    balances = relationship("UnspentBalance", back_populates="customer")
    consultant = relationship("Consultant", back_populates="customers")
    
    @hybrid_property
    def total_consumption(self):
        return sum([c.amount for c in self.consumptions])
    
    @hybrid_property
    def last_visit_days(self):
        from datetime import date
        return (date.today() - self.last_visit_date).days if self.last_visit_date else None

class Consultant(Base):
    __tablename__ = 'consultants'
    
    consultant_id = Column(Integer, primary_key=True, autoincrement=True, comment='咨询师编号')
    name = Column(String(50), nullable=False, comment='咨询师姓名')
    department = Column(Enum('皮肤科', '无创科', '整形外科'), nullable=False, comment='所属科室')
    
    # 关系定义
    customers = relationship("Customer", back_populates="consultant")
    consumptions = relationship("ConsumptionRecord", back_populates="consultant")
    write_offs = relationship("WriteOffRecord", back_populates="consultant")

class MedicalProduct(Base):
    __tablename__ = 'medical_products'
    
    product_id = Column(Integer, primary_key=True, autoincrement=True, comment='品项编号')
    product_name = Column(String(100), nullable=False, comment='品项名称')
    department = Column(Enum('皮肤科', '无创科', '整形外科', '综合'), nullable=False, comment='科室分类')
    product_type = Column(Enum('流量品', '利润品', '高价款'), nullable=False, comment='品项类型')
    standard_price = Column(Float, nullable=False, comment='标准价格')
    
    # 关系定义
    consumptions = relationship("ConsumptionRecord", back_populates="product")
    write_offs = relationship("WriteOffRecord", back_populates="product")
    balances = relationship("UnspentBalance", back_populates="product")

class ConsumptionRecord(Base):
    __tablename__ = 'consumption_records'
    
    record_id = Column(Integer, primary_key=True, autoincrement=True, comment='记录ID')
    customer_id = Column(Integer, ForeignKey('customers.customer_id'), nullable=False, comment='顾客编号')
    consume_date = Column(Date, nullable=False, comment='消费日期')
    amount = Column(Float, nullable=False, comment='消费金额')
    department = Column(Enum('皮肤科', '无创科', '整形外科', '综合'), nullable=False, comment='科室分类')
    is_new_customer = Column(Boolean, nullable=False, comment='新老标识')
    consultant_id = Column(Integer, ForeignKey('consultants.consultant_id'), nullable=False, comment='所属咨询')
    product_id = Column(Integer, ForeignKey('medical_products.product_id'), nullable=False, comment='品项名称')
    quantity = Column(Integer, default=1, comment='购买数量')
    payment_method = Column(Enum('现金', '银行卡', '分期', '医保'), default='现金', comment='支付方式')
    related_campaign = Column(String(100), comment='关联营销活动')
    
    # 关系定义
    customer = relationship("Customer", back_populates="consumptions")
    consultant = relationship("Consultant", back_populates="consumptions")
    product = relationship("MedicalProduct", back_populates="consumptions")
    write_offs = relationship("WriteOffRecord", back_populates="consumption")

class WriteOffRecord(Base):
    __tablename__ = 'write_off_records'
    
    write_off_id = Column(Integer, primary_key=True, autoincrement=True, comment='划扣ID')
    customer_id = Column(Integer, ForeignKey('customers.customer_id'), nullable=False, comment='顾客编号')
    write_off_date = Column(Date, nullable=False, comment='划扣日期')
    amount = Column(Float, nullable=False, comment='划扣金额')
    department = Column(Enum('皮肤科', '无创科', '整形外科', '综合'), nullable=False, comment='科室分类')
    product_id = Column(Integer, ForeignKey('medical_products.product_id'), nullable=False, comment='品项名称')
    quantity = Column(Integer, default=1, comment='划扣数量')
    consultant_id = Column(Integer, ForeignKey('consultants.consultant_id'), nullable=False, comment='所属咨询')
    consume_record_id = Column(Integer, ForeignKey('consumption_records.record_id'), nullable=False, comment='关联消费记录')
    write_off_type = Column(Enum('正常划扣', '活动核销', '套餐消耗'), default='正常划扣', comment='划扣类型')
    
    # 关系定义
    customer = relationship("Customer", back_populates="write_offs")
    consultant = relationship("Consultant", back_populates="write_offs")
    product = relationship("MedicalProduct", back_populates="write_offs")
    consumption = relationship("ConsumptionRecord", back_populates="write_offs")

class UnspentBalance(Base):
    __tablename__ = 'unspent_balances'
    
    balance_id = Column(Integer, primary_key=True, autoincrement=True, comment='余额ID')
    customer_id = Column(Integer, ForeignKey('customers.customer_id'), nullable=False, comment='顾客编号')
    product_id = Column(Integer, ForeignKey('medical_products.product_id'), nullable=False, comment='品项名称')
    total_amount = Column(Float, nullable=False, comment='总购买金额')
    spent_amount = Column(Float, default=0, comment='已划扣金额')
    last_write_off_date = Column(Date, comment='最后划扣日期')
    expiration_date = Column(Date, comment='有效期至')
    
    # 计算字段
    @hybrid_property
    def remaining_amount(self):
        return self.total_amount - self.spent_amount
    
    # 关系定义
    customer = relationship("Customer", back_populates="balances")
    product = relationship("MedicalProduct", back_populates="balances")

def init_db():
    """初始化数据库"""
    engine = get_engine()
    Base.metadata.create_all(engine)
    print("数据库初始化完成！") 