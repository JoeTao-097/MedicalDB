from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from decimal import Decimal

# 基础模型
class CustomerBase(BaseModel):
    name: str = Field(..., description="顾客姓名")
    phone: str = Field(..., description="联系电话")
    register_date: date = Field(..., description="注册日期")
    last_visit_date: Optional[date] = Field(None, description="最近到店日期")
    consultant_id: int = Field(..., description="专属咨询师ID")
    health_tags: Optional[Dict[str, Any]] = Field(None, description="健康标签")
    membership_level: str = Field("普通", description="会员等级")

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    last_visit_date: Optional[date] = None
    consultant_id: Optional[int] = None
    health_tags: Optional[Dict[str, Any]] = None
    membership_level: Optional[str] = None

class Customer(CustomerBase):
    customer_id: int
    total_consumption: Optional[Decimal] = None
    last_visit_days: Optional[int] = None
    
    class Config:
        from_attributes = True

# 咨询师模型
class ConsultantBase(BaseModel):
    name: str = Field(..., description="咨询师姓名")
    department: str = Field(..., description="所属科室")

class ConsultantCreate(ConsultantBase):
    pass

class ConsultantUpdate(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None

class Consultant(ConsultantBase):
    consultant_id: int
    
    class Config:
        from_attributes = True

# 产品模型
class MedicalProductBase(BaseModel):
    product_name: str = Field(..., description="品项名称")
    department: str = Field(..., description="科室分类")
    product_type: str = Field(..., description="品项类型")
    standard_price: Decimal = Field(..., description="标准价格")

class MedicalProductCreate(MedicalProductBase):
    pass

class MedicalProductUpdate(BaseModel):
    product_name: Optional[str] = None
    department: Optional[str] = None
    product_type: Optional[str] = None
    standard_price: Optional[Decimal] = None

class MedicalProduct(MedicalProductBase):
    product_id: int
    
    class Config:
        from_attributes = True

# 消费记录模型
class ConsumptionRecordBase(BaseModel):
    customer_id: int = Field(..., description="顾客编号")
    consume_date: date = Field(..., description="消费日期")
    amount: Decimal = Field(..., description="消费金额")
    department: str = Field(..., description="科室分类")
    is_new_customer: bool = Field(..., description="新老标识")
    consultant_id: int = Field(..., description="所属咨询师ID")
    product_id: int = Field(..., description="品项ID")
    quantity: int = Field(1, description="购买数量")
    payment_method: str = Field("现金", description="支付方式")
    related_campaign: Optional[str] = Field(None, description="关联营销活动")

class ConsumptionRecordCreate(ConsumptionRecordBase):
    pass

class ConsumptionRecordUpdate(BaseModel):
    consume_date: Optional[date] = None
    amount: Optional[Decimal] = None
    department: Optional[str] = None
    is_new_customer: Optional[bool] = None
    consultant_id: Optional[int] = None
    product_id: Optional[int] = None
    quantity: Optional[int] = None
    payment_method: Optional[str] = None
    related_campaign: Optional[str] = None

class ConsumptionRecord(ConsumptionRecordBase):
    record_id: int
    
    class Config:
        from_attributes = True

# 划扣记录模型
class WriteOffRecordBase(BaseModel):
    customer_id: int = Field(..., description="顾客编号")
    write_off_date: date = Field(..., description="划扣日期")
    amount: Decimal = Field(..., description="划扣金额")
    department: str = Field(..., description="科室分类")
    product_id: int = Field(..., description="品项ID")
    quantity: int = Field(1, description="划扣数量")
    consultant_id: int = Field(..., description="所属咨询师ID")
    consume_record_id: int = Field(..., description="关联消费记录ID")
    write_off_type: str = Field("正常划扣", description="划扣类型")

class WriteOffRecordCreate(WriteOffRecordBase):
    pass

class WriteOffRecordUpdate(BaseModel):
    write_off_date: Optional[date] = None
    amount: Optional[Decimal] = None
    department: Optional[str] = None
    product_id: Optional[int] = None
    quantity: Optional[int] = None
    consultant_id: Optional[int] = None
    write_off_type: Optional[str] = None

class WriteOffRecord(WriteOffRecordBase):
    write_off_id: int
    
    class Config:
        from_attributes = True

# 未划扣余额模型
class UnspentBalanceBase(BaseModel):
    customer_id: int = Field(..., description="顾客编号")
    product_id: int = Field(..., description="品项ID")
    total_amount: Decimal = Field(..., description="总购买金额")
    spent_amount: Decimal = Field(0, description="已划扣金额")
    last_write_off_date: Optional[date] = Field(None, description="最后划扣日期")
    expiration_date: Optional[date] = Field(None, description="有效期至")

class UnspentBalanceCreate(UnspentBalanceBase):
    pass

class UnspentBalanceUpdate(BaseModel):
    total_amount: Optional[Decimal] = None
    spent_amount: Optional[Decimal] = None
    last_write_off_date: Optional[date] = None
    expiration_date: Optional[date] = None

class UnspentBalance(UnspentBalanceBase):
    balance_id: int
    remaining_amount: Optional[Decimal] = None
    
    class Config:
        from_attributes = True

# 分析结果模型
class AnalysisResult(BaseModel):
    title: str
    description: str
    data: List[Dict[str, Any]]
    summary: Optional[str] = None

# 自然语言查询模型
class NaturalLanguageQuery(BaseModel):
    query: str = Field(..., description="自然语言查询")
    limit: Optional[int] = Field(100, description="结果限制数量")

class QueryResult(BaseModel):
    success: bool
    data: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
    sql: Optional[str] = None 