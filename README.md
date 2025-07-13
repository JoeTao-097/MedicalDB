# 医美数据管理系统

一个基于FastAPI和Streamlit的医疗美容数据管理系统，提供完整的数据管理、分析和自然语言查询功能。

## 🏗️ 项目结构

```
medical-cosmetics-analytics/
├── backend/                 # FastAPI 后端
│   ├── main.py              # FastAPI 主应用
│   ├── models.py            # 数据库模型
│   ├── schemas.py           # Pydantic 数据模型
│   ├── database.py          # 数据库连接
│   ├── text2sql.py          # Text2SQL 功能
│   ├── analysis.py          # 业务分析函数
│   └── requirements.txt     # 后端依赖
├── frontend/                # Streamlit 前端
│   ├── app.py               # 主应用
│   ├── pages/               # 多页面模块
│   │   ├── 1_自然语言查询.py
│   │   ├── 2_十大增长点分析.py
│   │   └── 3_数据管理.py
│   └── requirements.txt     # 前端依赖
├── env_example              # 环境变量示例
└── README.md                # 项目说明
```

## 🚀 快速开始

### 1. 环境准备

确保您的系统已安装：
- Python 3.8+
- MySQL 数据库
- Git

### 2. 克隆项目

```bash
git clone <repository-url>
cd medical-cosmetics-analytics
```

### 3. 环境配置

复制环境变量文件：
```bash
cp env_example .env
```

编辑 `.env` 文件，配置数据库和OpenAI API：
```env
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_NAME=medical_cosmetics
DB_USER=root
DB_PASSWORD=your_password

# OpenAI API配置
OPENAI_API_KEY=your_openai_api_key_here
```

### 4. 安装依赖

#### 后端依赖
```bash
cd backend
pip install -r requirements.txt
```

#### 前端依赖
```bash
cd frontend
pip install -r requirements.txt
```

### 5. 数据库初始化

```bash
cd backend
python -c "from models import init_db; init_db()"
```

### 6. 启动服务

#### 启动后端服务
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### 启动前端服务
```bash
cd frontend
streamlit run app.py --server.port 8501
```

### 7. 访问应用

- 前端界面：http://localhost:8501
- 后端API文档：http://localhost:8000/docs

## 📊 功能特性

### 核心功能

1. **数据管理**
   - 顾客信息管理
   - 咨询师管理
   - 产品管理
   - 消费记录管理
   - 划扣记录管理
   - 余额管理

2. **数据分析**
   - 不活跃顾客分析
   - 新客二开率分析
   - VIP顾客消费分析
   - 未划扣余额分析
   - 科室业绩分析
   - 产品表现分析

3. **自然语言查询**
   - 智能SQL转换
   - 多维度数据查询
   - 查询结果可视化

4. **增长点分析**
   - 十大增长机会识别
   - 优先级评估
   - 行动建议

### 技术特性

- **后端**: FastAPI + SQLAlchemy + MySQL
- **前端**: Streamlit + Plotly + Pandas
- **AI功能**: OpenAI GPT-4 Text2SQL
- **数据可视化**: 交互式图表
- **响应式设计**: 现代化UI界面

## 🗄️ 数据库设计

### 主要数据表

1. **customers** - 顾客信息表
   - customer_id: 顾客编号
   - name: 顾客姓名
   - phone: 联系电话
   - register_date: 注册日期
   - last_visit_date: 最近到店日期
   - consultant_id: 专属咨询师
   - health_tags: 健康标签
   - membership_level: 会员等级

2. **consultants** - 咨询师信息表
   - consultant_id: 咨询师编号
   - name: 咨询师姓名
   - department: 所属科室

3. **medical_products** - 产品信息表
   - product_id: 品项编号
   - product_name: 品项名称
   - department: 科室分类
   - product_type: 品项类型
   - standard_price: 标准价格

4. **consumption_records** - 消费记录表
   - record_id: 记录ID
   - customer_id: 顾客编号
   - consume_date: 消费日期
   - amount: 消费金额
   - department: 科室分类
   - is_new_customer: 新老标识
   - consultant_id: 所属咨询师
   - product_id: 品项名称
   - quantity: 购买数量
   - payment_method: 支付方式

5. **write_off_records** - 划扣记录表
   - write_off_id: 划扣ID
   - customer_id: 顾客编号
   - write_off_date: 划扣日期
   - amount: 划扣金额
   - department: 科室分类
   - product_id: 品项名称
   - quantity: 划扣数量
   - consultant_id: 所属咨询师
   - consume_record_id: 关联消费记录

6. **unspent_balances** - 未划扣余额表
   - balance_id: 余额ID
   - customer_id: 顾客编号
   - product_id: 品项名称
   - total_amount: 总购买金额
   - spent_amount: 已划扣金额
   - last_write_off_date: 最后划扣日期
   - expiration_date: 有效期至

## 🔧 API接口

### 主要接口

- `GET /api/customers` - 获取顾客列表
- `POST /api/customers` - 创建新顾客
- `GET /api/consultants` - 获取咨询师列表
- `POST /api/consultants` - 创建新咨询师
- `GET /api/products` - 获取产品列表
- `POST /api/products` - 创建新产品
- `GET /api/consumption-records` - 获取消费记录
- `POST /api/consumption-records` - 创建消费记录
- `POST /api/query` - 自然语言查询
- `GET /api/analysis/*` - 各种分析接口

## 📈 使用指南

### 1. 数据录入

1. 首先添加咨询师信息
2. 添加产品信息
3. 录入顾客信息
4. 记录消费和划扣数据

### 2. 数据分析

1. 访问"数据分析"页面
2. 选择需要的分析类型
3. 查看分析结果和图表
4. 下载分析报告

### 3. 自然语言查询

1. 访问"自然语言查询"页面
2. 输入您的问题（如"查询最近6个月没有消费的顾客"）
3. 系统自动生成SQL并执行
4. 查看查询结果

### 4. 增长点分析

1. 访问"十大增长点分析"页面
2. 系统自动分析各种增长机会
3. 查看优先级排序的建议
4. 制定具体的行动计划

## 🛠️ 开发指南

### 添加新的分析功能

1. 在 `backend/analysis.py` 中添加新的分析函数
2. 在 `backend/main.py` 中添加对应的API接口
3. 在前端页面中集成新的分析功能

### 扩展数据模型

1. 在 `backend/models.py` 中定义新的数据模型
2. 在 `backend/schemas.py` 中添加对应的Pydantic模型
3. 在 `backend/main.py` 中添加CRUD接口
4. 在前端添加对应的管理页面

### 自定义查询

1. 在 `backend/text2sql.py` 中优化提示词
2. 添加新的查询示例
3. 测试查询准确性

## 🐛 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查数据库服务是否启动
   - 验证数据库配置信息
   - 确认数据库用户权限

2. **API请求失败**
   - 检查后端服务是否启动
   - 验证API地址和端口
   - 查看后端日志

3. **自然语言查询不准确**
   - 检查OpenAI API配置
   - 优化提示词模板
   - 验证数据库结构

4. **前端页面加载慢**
   - 检查网络连接
   - 优化数据查询
   - 减少不必要的数据传输

## 📝 更新日志

### v1.0.0 (2024-01-01)
- 初始版本发布
- 基础数据管理功能
- 核心分析功能
- 自然语言查询
- 增长点分析

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 项目Issues: [GitHub Issues](https://github.com/your-repo/issues)
- 邮箱: your-email@example.com

---

**注意**: 请确保在生产环境中使用前，充分测试所有功能并配置适当的安全措施。 