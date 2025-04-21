from sqlalchemy import Column, Integer, String, DateTime, select, update
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config.config import get_mysql_url
from sqlalchemy import create_engine
from datetime import datetime

# 创建数据库引擎
engine = create_engine(get_mysql_url(), echo=False)

# 创建基础类
Base = declarative_base()

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 定义 manhuaconfig 表的 ORM 模型
class ManhuaConfig(Base):
    __tablename__ = 'manhuaconfig'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    kname = Column(String(255), nullable=False)
    kvalue = Column(String(255), nullable=False)
    ktype = Column(String(255), nullable=True)
    ktypech = Column(String(255), nullable=True)
    updatetime = Column(DateTime, nullable=True)  # 新增字段：更新时间

# 查询指定 kname 的配置值
def get_config_value(kname: str) -> str:
    """
    从 manhuaconfig 表中查询指定 kname 的配置值。
    :param kname: 配置项的键名
    :return: 配置项的值
    """
    with SessionLocal() as session:
        result = session.execute(select(ManhuaConfig.kvalue).where(ManhuaConfig.kname == kname)).scalar()
        if not result:
            raise ValueError(f"未找到配置项：{kname}")
        return result

# 查询指定 kname 的配置值及更新时间
def get_token_with_updatetime(kname: str) -> dict:
    """
    查询指定 kname 的配置值及更新时间。
    :param kname: 配置项的键名
    :return: 包含 kvalue 和 updatetime 的字典
    """
    with SessionLocal() as session:
        result = session.execute(
            select(ManhuaConfig.kvalue, ManhuaConfig.updatetime).where(ManhuaConfig.kname == kname)
        ).first()
        if not result:
            return None
        return {"kvalue": result.kvalue, "updatetime": result.updatetime}

# 更新指定 kname 的 token 和更新时间
def update_token(kname: str, token: str) -> None:
    """
    更新指定 kname 的 token 和更新时间。
    :param kname: 配置项的键名
    :param token: 新的 token 值
    """
    with SessionLocal() as session:
        session.execute(
            update(ManhuaConfig)
            .where(ManhuaConfig.kname == kname)
            .values(kvalue=token, updatetime=datetime.now())
        )
        session.commit()
