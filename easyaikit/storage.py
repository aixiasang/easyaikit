"""
会话存储管理模块 - 提供数据库和 JSON 文件存储支持
"""

import os
import json
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any, Union

from sqlalchemy import create_engine, Column, String, Integer, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()


class Session(Base):
    """会话记录表"""
    __tablename__ = 'sessions'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(36), unique=True, nullable=False)  # UUID
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    system_message = Column(String, nullable=True)
    model = Column(String, nullable=True)
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")


class Message(Base):
    """消息记录表"""
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(36), ForeignKey('sessions.session_id'), nullable=False)
    role = Column(String(20), nullable=False)  # system, user, assistant
    content = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    extra_data = Column(JSON, nullable=True)  # 存储额外的消息元数据
    
    session = relationship("Session", back_populates="messages")


class DBStorage:
    """数据库存储管理器"""
    
    def __init__(
        self,
        db_path: str,
        db_type: str = "sqlite",
        table_prefix: str = "ai_message",
        session_id: Optional[str] = None
    ):
        """
        初始化存储管理器
        
        参数:
            db_path: 数据库路径
            db_type: 数据库类型，目前支持 sqlite
            table_prefix: 表名前缀
            session_id: 指定的会话ID，如果为 None 则创建新的
        """
        self.db_path = db_path
        self.db_type = db_type
        self.table_prefix = table_prefix
        self.session_id = session_id or str(uuid.uuid4())
        
        # 创建数据库连接
        if db_type == "sqlite":
            self.engine = create_engine(f'sqlite:///{db_path}')
        else:
            raise ValueError(f"不支持的数据库类型: {db_type}")
        
        # 创建表
        Base.metadata.create_all(self.engine)
        
        # 创建会话工厂
        self.Session = sessionmaker(bind=self.engine)
        
        # 如果提供了 session_id，验证其存在性
        if session_id:
            with self.Session() as db_session:
                session = db_session.query(Session).filter_by(session_id=session_id).first()
                if not session:
                    raise ValueError(f"找不到指定的会话ID: {session_id}")
    
    def save_message(
        self,
        role: str,
        content: str,
        system_message: Optional[str] = None,
        model: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        保存一条消息
        
        参数:
            role: 消息角色 (system/user/assistant)
            content: 消息内容
            system_message: 系统消息
            model: 使用的模型
            metadata: 额外的元数据
        """
        with self.Session() as db_session:
            # 获取或创建会话
            session = db_session.query(Session).filter_by(session_id=self.session_id).first()
            if not session:
                session = Session(
                    session_id=self.session_id,
                    system_message=system_message,
                    model=model
                )
                db_session.add(session)
            
            # 创建消息
            message = Message(
                session_id=self.session_id,
                role=role,
                content=content,
                extra_data=metadata
            )
            db_session.add(message)
            db_session.commit()
    
    def load_messages(self) -> List[Dict[str, str]]:
        """
        加载当前会话的所有消息
        
        返回:
            消息列表，格式为 [{"role": "...", "content": "..."}, ...]
        """
        with self.Session() as db_session:
            messages = (
                db_session.query(Message)
                .filter_by(session_id=self.session_id)
                .order_by(Message.created_at)
                .all()
            )
            return [{"role": msg.role, "content": msg.content} for msg in messages]
    
    def view_sessions(self) -> List[Dict[str, Any]]:
        """
        查看所有会话
        
        返回:
            会话列表，包含会话ID、创建时间等信息
        """
        with self.Session() as db_session:
            sessions = db_session.query(Session).order_by(Session.created_at.desc()).all()
            return [{
                "session_id": s.session_id,
                "created_at": s.created_at,
                "updated_at": s.updated_at,
                "system_message": s.system_message,
                "model": s.model,
                "message_count": len(s.messages)
            } for s in sessions]
    
    def view_session_messages(self, session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        查看指定会话的所有消息
        
        参数:
            session_id: 会话ID，如果为 None 则使用当前会话
            
        返回:
            消息列表，包含详细信息
        """
        target_session_id = session_id or self.session_id
        with self.Session() as db_session:
            messages = (
                db_session.query(Message)
                .filter_by(session_id=target_session_id)
                .order_by(Message.created_at)
                .all()
            )
            return [{
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at,
                "metadata": msg.extra_data
            } for msg in messages]
    
    def load_session(self, session_id: str, update: bool = False) -> str:
        """
        加载指定的会话
        
        参数:
            session_id: 要加载的会话ID
            update: 是否创建新的会话ID
            
        返回:
            当前使用的会话ID
        """
        with self.Session() as db_session:
            session = db_session.query(Session).filter_by(session_id=session_id).first()
            if not session:
                raise ValueError(f"找不到指定的会话ID: {session_id}")
            
            if update:
                # 创建新的会话ID
                self.session_id = str(uuid.uuid4())
            else:
                # 使用指定的会话ID
                self.session_id = session_id
            
            return self.session_id
    
    def clear_session(self) -> None:
        """清除当前会话的所有消息"""
        with self.Session() as db_session:
            db_session.query(Message).filter_by(session_id=self.session_id).delete()
            db_session.commit()


class JSONStorage:
    """JSON 文件存储管理器"""
    
    def __init__(
        self,
        file_path: str,
        session_id: Optional[str] = None
    ):
        """
        初始化 JSON 存储管理器
        
        参数:
            file_path: JSON 文件路径
            session_id: 指定的会话ID，如果为 None 则创建新的
        """
        self.file_path = file_path
        self.session_id = session_id or str(uuid.uuid4())
        
        # 确保文件存在
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump({"sessions": {}}, f)
        
        # 加载数据
        with open(file_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        # 初始化会话数据结构
        if "sessions" not in self.data:
            self.data["sessions"] = {}
        
        # 如果提供了 session_id，验证其存在性
        if session_id and session_id not in self.data["sessions"]:
            raise ValueError(f"找不到指定的会话ID: {session_id}")
    
    def _save(self) -> None:
        """保存数据到文件"""
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def save_message(
        self,
        role: str,
        content: str,
        system_message: Optional[str] = None,
        model: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        保存一条消息
        
        参数:
            role: 消息角色 (system/user/assistant)
            content: 消息内容
            system_message: 系统消息
            model: 使用的模型
            metadata: 额外的元数据
        """
        if self.session_id not in self.data["sessions"]:
            self.data["sessions"][self.session_id] = {
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "system_message": system_message,
                "model": model,
                "messages": []
            }
        
        session = self.data["sessions"][self.session_id]
        session["messages"].append({
            "role": role,
            "content": content,
            "created_at": datetime.utcnow().isoformat(),
            "metadata": metadata
        })
        session["updated_at"] = datetime.utcnow().isoformat()
        
        self._save()
    
    def load_messages(self) -> List[Dict[str, str]]:
        """
        加载当前会话的所有消息
        
        返回:
            消息列表，格式为 [{"role": "...", "content": "..."}, ...]
        """
        if self.session_id not in self.data["sessions"]:
            return []
        
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in self.data["sessions"][self.session_id]["messages"]
        ]
    
    def view_sessions(self) -> List[Dict[str, Any]]:
        """
        查看所有会话
        
        返回:
            会话列表，包含会话ID、创建时间等信息
        """
        return [{
            "session_id": sid,
            "created_at": session["created_at"],
            "updated_at": session["updated_at"],
            "system_message": session.get("system_message"),
            "model": session.get("model"),
            "message_count": len(session["messages"])
        } for sid, session in self.data["sessions"].items()]
    
    def view_session_messages(self, session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        查看指定会话的所有消息
        
        参数:
            session_id: 会话ID，如果为 None 则使用当前会话
            
        返回:
            消息列表，包含详细信息
        """
        target_session_id = session_id or self.session_id
        if target_session_id not in self.data["sessions"]:
            return []
        
        return self.data["sessions"][target_session_id]["messages"]
    
    def load_session(self, session_id: str, update: bool = False) -> str:
        """
        加载指定的会话
        
        参数:
            session_id: 要加载的会话ID
            update: 是否创建新的会话ID
            
        返回:
            当前使用的会话ID
        """
        if session_id not in self.data["sessions"]:
            raise ValueError(f"找不到指定的会话ID: {session_id}")
        
        if update:
            # 创建新的会话ID
            self.session_id = str(uuid.uuid4())
        else:
            # 使用指定的会话ID
            self.session_id = session_id
        
        return self.session_id
    
    def clear_session(self) -> None:
        """清除当前会话的所有消息"""
        if self.session_id in self.data["sessions"]:
            self.data["sessions"][self.session_id]["messages"] = []
            self.data["sessions"][self.session_id]["updated_at"] = datetime.utcnow().isoformat()
            self._save() 