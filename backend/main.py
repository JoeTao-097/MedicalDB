from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn

from database import get_session
from models import Customer, Consultant, MedicalProduct, ConsumptionRecord, WriteOffRecord, UnspentBalance
from schemas import (
    CustomerCreate, CustomerUpdate, Customer as CustomerSchema,
    ConsultantCreate, ConsultantUpdate, Consultant as ConsultantSchema,
    MedicalProductCreate, MedicalProductUpdate, MedicalProduct as MedicalProductSchema,
    ConsumptionRecordCreate, ConsumptionRecordUpdate, ConsumptionRecord as ConsumptionRecordSchema,
    WriteOffRecordCreate, WriteOffRecordUpdate, WriteOffRecord as WriteOffRecordSchema,
    UnspentBalanceCreate, UnspentBalanceUpdate, UnspentBalance as UnspentBalanceSchema,
    NaturalLanguageQuery, QueryResult, AnalysisResult
)
from text2sql import natural_language_query
from analysis import (
    analyze_inactive_customers, analyze_new_customer_reopen, analyze_vip_consumption,
    analyze_unspent_balance, analyze_department_performance, analyze_product_performance
)

app = FastAPI(
    title="医美数据管理系统API",
    description="医疗美容数据管理系统的后端API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 依赖注入
def get_db():
    db = get_session()
    try:
        yield db
    finally:
        db.close()

# 健康检查
@app.get("/")
async def root():
    return {"message": "医美数据管理系统API运行正常"}

# 自然语言查询API
@app.post("/api/query", response_model=QueryResult)
async def natural_language_query_api(query: NaturalLanguageQuery):
    """自然语言查询接口"""
    result = natural_language_query(query.query)
    return QueryResult(**result)

# 分析API
@app.get("/api/analysis/inactive-customers")
async def get_inactive_customers_analysis(months: int = 6):
    """获取不活跃顾客分析"""
    return analyze_inactive_customers(months)

@app.get("/api/analysis/new-customer-reopen")
async def get_new_customer_reopen_analysis():
    """获取新客二开率分析"""
    return analyze_new_customer_reopen()

@app.get("/api/analysis/vip-consumption")
async def get_vip_consumption_analysis():
    """获取VIP顾客消费分析"""
    return analyze_vip_consumption()

@app.get("/api/analysis/unspent-balance")
async def get_unspent_balance_analysis():
    """获取未划扣余额分析"""
    return analyze_unspent_balance()

@app.get("/api/analysis/department-performance")
async def get_department_performance_analysis():
    """获取科室业绩分析"""
    return analyze_department_performance()

@app.get("/api/analysis/product-performance")
async def get_product_performance_analysis():
    """获取产品表现分析"""
    return analyze_product_performance()

# 顾客管理API
@app.get("/api/customers", response_model=List[CustomerSchema])
async def get_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取顾客列表"""
    customers = db.query(Customer).offset(skip).limit(limit).all()
    return customers

@app.get("/api/customers/{customer_id}", response_model=CustomerSchema)
async def get_customer(customer_id: int, db: Session = Depends(get_db)):
    """获取单个顾客信息"""
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if customer is None:
        raise HTTPException(status_code=404, detail="顾客不存在")
    return customer

@app.post("/api/customers", response_model=CustomerSchema)
async def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    """创建新顾客"""
    db_customer = Customer(**customer.dict())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

@app.put("/api/customers/{customer_id}", response_model=CustomerSchema)
async def update_customer(customer_id: int, customer: CustomerUpdate, db: Session = Depends(get_db)):
    """更新顾客信息"""
    db_customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if db_customer is None:
        raise HTTPException(status_code=404, detail="顾客不存在")
    
    update_data = customer.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_customer, field, value)
    
    db.commit()
    db.refresh(db_customer)
    return db_customer

@app.delete("/api/customers/{customer_id}")
async def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    """删除顾客"""
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if customer is None:
        raise HTTPException(status_code=404, detail="顾客不存在")
    
    db.delete(customer)
    db.commit()
    return {"message": "顾客删除成功"}

# 咨询师管理API
@app.get("/api/consultants", response_model=List[ConsultantSchema])
async def get_consultants(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取咨询师列表"""
    consultants = db.query(Consultant).offset(skip).limit(limit).all()
    return consultants

@app.post("/api/consultants", response_model=ConsultantSchema)
async def create_consultant(consultant: ConsultantCreate, db: Session = Depends(get_db)):
    """创建新咨询师"""
    db_consultant = Consultant(**consultant.dict())
    db.add(db_consultant)
    db.commit()
    db.refresh(db_consultant)
    return db_consultant

# 产品管理API
@app.get("/api/products", response_model=List[MedicalProductSchema])
async def get_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取产品列表"""
    products = db.query(MedicalProduct).offset(skip).limit(limit).all()
    return products

@app.post("/api/products", response_model=MedicalProductSchema)
async def create_product(product: MedicalProductCreate, db: Session = Depends(get_db)):
    """创建新产品"""
    db_product = MedicalProduct(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

# 消费记录管理API
@app.get("/api/consumption-records", response_model=List[ConsumptionRecordSchema])
async def get_consumption_records(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取消费记录列表"""
    records = db.query(ConsumptionRecord).offset(skip).limit(limit).all()
    return records

@app.post("/api/consumption-records", response_model=ConsumptionRecordSchema)
async def create_consumption_record(record: ConsumptionRecordCreate, db: Session = Depends(get_db)):
    """创建新消费记录"""
    db_record = ConsumptionRecord(**record.dict())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

# 划扣记录管理API
@app.get("/api/write-off-records", response_model=List[WriteOffRecordSchema])
async def get_write_off_records(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取划扣记录列表"""
    records = db.query(WriteOffRecord).offset(skip).limit(limit).all()
    return records

@app.post("/api/write-off-records", response_model=WriteOffRecordSchema)
async def create_write_off_record(record: WriteOffRecordCreate, db: Session = Depends(get_db)):
    """创建新划扣记录"""
    db_record = WriteOffRecord(**record.dict())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

# 未划扣余额管理API
@app.get("/api/unspent-balances", response_model=List[UnspentBalanceSchema])
async def get_unspent_balances(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取未划扣余额列表"""
    balances = db.query(UnspentBalance).offset(skip).limit(limit).all()
    return balances

@app.post("/api/unspent-balances", response_model=UnspentBalanceSchema)
async def create_unspent_balance(balance: UnspentBalanceCreate, db: Session = Depends(get_db)):
    """创建新未划扣余额记录"""
    db_balance = UnspentBalance(**balance.dict())
    db.add(db_balance)
    db.commit()
    db.refresh(db_balance)
    return db_balance

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 