from sqlalchemy import Column, String, ForeignKey, JSON, Integer, Index
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from typing import TYPE_CHECKING

# Base를 타입 힌트로 사용하지 않음 (mypy 오류 방지)
Base = declarative_base()

DUMMY_ROOT_ID = "__DUMMY_ROOT_ID__"
# PostgreSQL의 경우, AUTOINCREMENT 기본 키에 Integer를 사용하는 것이 일반적입니다.
# 하지만 기존 ID가 문자열일 수 있으므로, String ID를 유지하되, 순서를 위한 필드를 추가할 수 있습니다.
# 여기서는 ID 자체를 문자열 기본키로 유지하고, 순서는 관계 또는 별도 필드로 관리한다고 가정합니다.

class MTItem(Base):  # type: ignore
    __tablename__ = 'mt_items'

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, default='New Item')
    data = Column(JSON, nullable=True) # PostgreSQL에서는 JSONB 타입을 고려할 수 있습니다.

    parent_id = Column(String, ForeignKey('mt_items.id'), nullable=True, index=True)
    
    # 아이템 순서를 위한 필드 (옵션)
    # PostgreSQL에서는 array 타입이나, 별도의 순서 테이블, 또는 정렬 가능한 필드를 사용할 수 있습니다.
    # 여기서는 order 필드를 추가하여 부모 내에서의 순서를 관리하도록 합니다.
    item_order = Column(Integer, nullable=False, default=0)

    parent = relationship("MTItem", remote_side=[id], back_populates="children", lazy='select')
    children = relationship(
        "MTItem", 
        back_populates="parent", 
        cascade="all, delete-orphan", 
        lazy='select',
        order_by="MTItem.item_order" # children 로드 시 item_order 기준으로 정렬
    )

    # sibling_order가 동일한 경우를 대비하여 parent_id와 item_order에 대한 복합 인덱스
    __table_args__ = (
        Index('idx_parent_order', 'parent_id', 'item_order'),
    )

    def __repr__(self):
        return f"<MTItem(id='{self.id}', name='{self.name}', parent_id='{self.parent_id}', order={self.item_order})>"

    @hybrid_property
    def is_dummy_root(self):
        return self.id == DUMMY_ROOT_ID

    def to_dict(self, include_children: bool = True) -> dict:
        item_dict = {
            'id': self.id,
            'name': self.name,
            'data': self.data if self.data is not None else {},
            'parent_id': self.parent_id,
            'item_order': self.item_order
        }
        if include_children and self.children:
            item_dict['children'] = sorted([child.to_dict(include_children=True) for child in self.children], key=lambda x: x['item_order'])
        else:
            item_dict['children'] = []
        return item_dict

    @classmethod
    def from_dict(cls, data: dict, session, parent_id: str | None = None):
        # 이 메서드는 SQLAlchemy ORM에서는 직접 사용하기보다, 
        # Repository 레벨에서 데이터를 받아 MTItem 객체를 생성하고 세션에 추가하는 방식으로 처리됩니다.
        # dict로부터 객체를 재귀적으로 생성하는 로직이 필요하다면 Repository에서 구현하는 것이 좋습니다.
        pass 