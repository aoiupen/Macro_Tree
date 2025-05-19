import uuid
import logging
from typing import Any, Dict, List, Optional

from sqlalchemy import func, and_, or_
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy.exc import SQLAlchemyError

from model.store.db.models import MTItem, DUMMY_ROOT_ID
from model.store.db.database_setup import get_db_session
from model.store.repo.interfaces.base_tree_repo import IMTStore
import core.exceptions as exc # 사용자 정의 예외 사용 (경로 확인 필요)

logger = logging.getLogger(__name__)

class SQLAlchemyTreeRepo(IMTStore):
    """SQLAlchemy ORM 기반 트리 저장소 구현체"""

    def __init__(self):
        # self.db_session_factory = get_db_session # 필요시 팩토리 형태로 주입받을 수 있음
        pass

    def _generate_id(self) -> str:
        return str(uuid.uuid4())

    def ensure_dummy_root(self) -> MTItem:
        with get_db_session() as db:
            try:
                dummy_root = db.query(MTItem).filter(MTItem.id == DUMMY_ROOT_ID).first()
                if not dummy_root:
                    logger.info(f"Creating dummy root node with ID: {DUMMY_ROOT_ID}")
                    dummy_root = MTItem(
                        id=DUMMY_ROOT_ID, 
                        name="__DUMMY_ROOT__", 
                        parent_id=None, # 더미 루트는 부모가 없음
                        item_order=0
                    )
                    db.add(dummy_root)
                    db.commit()
                    db.refresh(dummy_root)
                return dummy_root
            except SQLAlchemyError as e:
                db.rollback()
                logger.error(f"Error ensuring dummy root: {e}")
                raise exc.RepositoryError(f"Failed to ensure dummy root: {e}")

    def get_item(self, item_id: str) -> Optional[MTItem]:
        if not item_id:
            return None
        with get_db_session() as db:
            try:
                # 자식까지 함께 로드하려면 options(selectinload(MTItem.children)) 등을 사용
                item = db.query(MTItem).filter(MTItem.id == item_id).first()
                return item
            except SQLAlchemyError as e:
                logger.error(f"Error getting item '{item_id}': {e}")
                # raise exc.RepositoryError(f"Failed to get item '{item_id}': {e}") # 예외 발생시 None 반환
                return None

    def get_children(self, parent_id: Optional[str]) -> List[MTItem]:
        target_parent_id = parent_id if parent_id is not None else DUMMY_ROOT_ID
        with get_db_session() as db:
            try:
                children = (
                    db.query(MTItem)
                    .filter(MTItem.parent_id == target_parent_id)
                    .order_by(MTItem.item_order)
                    .all()
                )
                return children
            except SQLAlchemyError as e:
                logger.error(f"Error getting children for parent '{target_parent_id}': {e}")
                return []

    def get_all_items_in_tree(self) -> List[MTItem]:
        """더미 루트를 제외한 모든 아이템을 반환합니다."""
        with get_db_session() as db:
            try:
                items = (
                    db.query(MTItem)
                    .filter(MTItem.id != DUMMY_ROOT_ID) # 더미 루트 제외
                    .order_by(MTItem.parent_id, MTItem.item_order) # 부모, 순서대로 정렬 (옵션)
                    .all()
                )
                return items
            except SQLAlchemyError as e:
                logger.error(f"Error getting all items in tree: {e}")
                return []

    def _get_next_order(self, db: Session, parent_id: Optional[str]) -> int:
        """주어진 부모 내에서 다음 아이템 순서를 계산합니다."""
        max_order = (
            db.query(func.max(MTItem.item_order))
            .filter(MTItem.parent_id == parent_id)
            .scalar()
        )
        return (max_order + 1) if max_order is not None else 0

    def add_item(self, 
                 name: str, 
                 parent_id: Optional[str], 
                 item_order: Optional[int] = None, # item_order는 필수로 받거나, None이면 자동계산
                 data: Optional[Dict[str, Any]] = None, 
                 specific_id: Optional[str] = None) -> MTItem:
        
        actual_parent_id = parent_id if parent_id is not None else DUMMY_ROOT_ID
        
        with get_db_session() as db:
            try:
                # 부모가 DUMMY_ROOT_ID가 아니고, 실제 존재하는지 확인 (옵션)
                if actual_parent_id != DUMMY_ROOT_ID:
                    parent_item = db.query(MTItem.id).filter(MTItem.id == actual_parent_id).first()
                    if not parent_item:
                        raise exc.ParentItemNotFoundError(f"Parent item with id '{actual_parent_id}' not found.")

                item_id = specific_id if specific_id else self._generate_id()

                # item_order 처리: 명시적 제공 시 사용, 아니면 자동 계산
                if item_order is None:
                    order_to_use = self._get_next_order(db, actual_parent_id)
                else:
                    # 만약 item_order가 제공되면, 해당 순서에 이미 아이템이 있는지,
                    # 있다면 기존 아이템들의 순서를 조정할지 등을 결정해야 합니다.
                    # 여기서는 우선 제공된 값을 사용하고, 필요시 순서 조정 로직 추가.
                    # 여기서는 일단 중복을 허용하지 않고, 뒤로 밀어내는 로직을 가정해봅니다.
                    # (실제로는 더 복잡한 순서 관리 로직이 필요할 수 있음)
                    self._shift_items_for_insert(db, actual_parent_id, item_order)
                    order_to_use = item_order

                new_item = MTItem(
                    id=item_id,
                    name=name,
                    parent_id=actual_parent_id,
                    item_order=order_to_use,
                    data=data
                )
                db.add(new_item)
                db.commit()
                db.refresh(new_item)
                return new_item
            except SQLAlchemyError as e:
                db.rollback()
                logger.error(f"Error adding item '{name}': {e}")
                raise exc.RepositoryError(f"Failed to add item '{name}': {e}")
    
    def _shift_items_for_insert(self, db: Session, parent_id: Optional[str], start_order: int):
        """새 아이템 삽입을 위해 기존 아이템들의 순서를 뒤로 한 칸씩 민다."""
        db.query(MTItem).filter(
            MTItem.parent_id == parent_id,
            MTItem.item_order >= start_order
        ).update({MTItem.item_order: MTItem.item_order + 1}, synchronize_session=False)

    def _shift_items_for_delete(self, db: Session, parent_id: Optional[str], deleted_order: int):
        """아이템 삭제 후 기존 아이템들의 순서를 앞으로 한 칸씩 당긴다."""
        db.query(MTItem).filter(
            MTItem.parent_id == parent_id,
            MTItem.item_order > deleted_order
        ).update({MTItem.item_order: MTItem.item_order - 1}, synchronize_session=False)

    def update_item(self, 
                    item_id: str, 
                    name: Optional[str] = None, 
                    data: Optional[Dict[str, Any]] = None,
                    item_order: Optional[int] = None # 순서 변경은 move_item을 통하는 것을 권장
                    ) -> Optional[MTItem]:
        if not item_id or item_id == DUMMY_ROOT_ID: # 더미 루트는 수정 불가
            return None
            
        with get_db_session() as db:
            try:
                item = db.query(MTItem).filter(MTItem.id == item_id).first()
                if not item:
                    # raise exc.ItemNotFoundError(f"Item with id '{item_id}' not found for update.")
                    return None

                updated = False
                if name is not None:
                    item.name = name
                    updated = True
                if data is not None: # data 필드가 None으로 설정될 수도 있으므로 명시적 체크
                    item.data = data
                    updated = True
                
                # item_order 변경은 복잡성을 야기하므로 별도 move_item 메서드에서 처리하는 것이 좋음.
                # 만약 여기서 순서 변경을 허용한다면, 기존 아이템들과의 순서 조정 로직 필요.
                if item_order is not None and item.item_order != item_order:
                    # 이 경우, 기존 위치에서 아이템을 제거하고 새 위치로 삽입하는 것과 유사한 처리 필요
                    # (현재 부모 내에서 순서만 변경하는 경우)
                    old_parent_id = item.parent_id
                    old_order = item.item_order
                    
                    self._shift_items_for_delete(db, old_parent_id, old_order)
                    self._shift_items_for_insert(db, old_parent_id, item_order)
                    item.item_order = item_order
                    updated = True

                if updated:
                    db.commit()
                    db.refresh(item)
                return item
            except SQLAlchemyError as e:
                db.rollback()
                logger.error(f"Error updating item '{item_id}': {e}")
                raise exc.RepositoryError(f"Failed to update item '{item_id}': {e}")

    def _delete_recursive(self, db: Session, item_id: str):
        """특정 아이템과 그 모든 자식 아이템들을 재귀적으로 삭제 목록에 추가 (실제 삭제는 아님)"""
        # 주의: 이 방식은 매우 많은 자식이 있을 경우 재귀 깊이 제한이나 성능 문제를 일으킬 수 있음
        # 대안: CTE를 사용한 재귀적 삭제 SQL 실행 (PostgreSQL의 경우 WITH RECURSIVE 사용)
        item_to_delete = db.query(MTItem).filter(MTItem.id == item_id).first()
        if not item_to_delete:
            return

        # 자식들을 먼저 재귀적으로 삭제 처리
        children = db.query(MTItem.id).filter(MTItem.parent_id == item_id).all()
        for child_tuple in children:
            self._delete_recursive(db, child_tuple[0]) # 자식 ID로 재귀 호출
        
        # 현재 아이템 삭제
        db.delete(item_to_delete)
        # 삭제 후 순서 조정은 delete_item의 메인 로직에서 처리

    def delete_item(self, item_id: str) -> bool:
        if not item_id or item_id == DUMMY_ROOT_ID: # 더미 루트는 삭제 불가
            return False

        with get_db_session() as db:
            try:
                item_to_delete = db.query(MTItem).filter(MTItem.id == item_id).first()
                if not item_to_delete:
                    # raise exc.ItemNotFoundError(f"Item with id '{item_id}' not found for deletion.")
                    return False
                
                parent_id_of_deleted = item_to_delete.parent_id
                order_of_deleted = item_to_delete.item_order

                # 1. CTE를 사용한 재귀 삭제 (PostgreSQL 권장 방식)
                # 이 방식은 _delete_recursive 헬퍼 대신 사용됩니다.
                # MTItem 모델에 children 관계가 cascade="all, delete-orphan"으로 설정되어 있으므로,
                # 부모를 삭제하면 SQLAlchemy가 자식들도 ORM 레벨에서 처리하려고 시도합니다.
                # 하지만 순수한 DB 레벨 재귀 삭제가 더 효율적일 수 있습니다.
                # 여기서는 cascade delete-orphan을 활용하고, 순서만 조정합니다.
                
                # 자식 아이템들을 가져와서 (나중에 이벤트 발생 등에 사용 가능)
                # descendant_ids = self._get_all_descendant_ids(db, item_id)
                
                db.delete(item_to_delete) # cascade delete-orphan에 의해 자식들도 삭제됨
                
                # 삭제된 아이템과 같은 부모를 가진 형제들의 순서를 조정
                if parent_id_of_deleted: # 더미 루트의 직계 자식이 아닌 경우
                    self._shift_items_for_delete(db, parent_id_of_deleted, order_of_deleted)
                
                db.commit()
                return True
            except SQLAlchemyError as e:
                db.rollback()
                logger.error(f"Error deleting item '{item_id}': {e}")
                # raise exc.RepositoryError(f"Failed to delete item '{item_id}': {e}")
                return False

    def move_item(self, 
                  item_id: str, 
                  new_parent_id: Optional[str],
                  new_order: int) -> Optional[MTItem]:
        if not item_id or item_id == DUMMY_ROOT_ID:
            return None

        actual_new_parent_id = new_parent_id if new_parent_id is not None else DUMMY_ROOT_ID

        with get_db_session() as db:
            try:
                item_to_move = db.query(MTItem).filter(MTItem.id == item_id).first()
                if not item_to_move:
                    # raise exc.ItemNotFoundError(f"Item to move (id: '{item_id}') not found.")
                    return None

                if item_to_move.id == actual_new_parent_id: # 자기 자신을 부모로 설정 불가
                    raise exc.InvalidOperationError("Cannot move item to be a child of itself.")

                # 새 부모가 실제 존재하는지 확인 (더미 루트 제외)
                if actual_new_parent_id != DUMMY_ROOT_ID:
                    new_parent_obj = db.query(MTItem.id).filter(MTItem.id == actual_new_parent_id).first()
                    if not new_parent_obj:
                        raise exc.ParentItemNotFoundError(f"New parent item (id: '{actual_new_parent_id}') not found.")
                    # 이동 대상 아이템이 새 부모의 상위 아이템인지 확인 (순환 참조 방지)
                    ancestor = db.query(MTItem).filter(MTItem.id == actual_new_parent_id).first()
                    while ancestor:
                        if ancestor.parent_id == item_to_move.id:
                            raise exc.InvalidOperationError("Cannot move item to one of its own descendants.")
                        if not ancestor.parent_id: # 더미 루트의 직계 자식이면 더 이상 올라갈 곳 없음
                            break
                        ancestor = db.query(MTItem).filter(MTItem.id == ancestor.parent_id).first()
                        if ancestor and ancestor.id == DUMMY_ROOT_ID: # 더미루트에 도달하면 종료
                            break
                
                old_parent_id = item_to_move.parent_id
                old_order = item_to_move.item_order

                # 1. 이전 위치에서 아이템 순서 조정
                if old_parent_id is not None: # 이전 부모가 더미루트가 아닌 경우에도 동작 (parent_id가 None일 수 없음, 항상 DUMMY_ROOT_ID의 자식임)
                    self._shift_items_for_delete(db, old_parent_id, old_order)

                # 2. 새 위치에 아이템 삽입을 위한 순서 조정
                self._shift_items_for_insert(db, actual_new_parent_id, new_order)

                # 3. 아이템의 부모 및 순서 업데이트
                item_to_move.parent_id = actual_new_parent_id
                item_to_move.item_order = new_order
                
                db.commit()
                db.refresh(item_to_move)
                return item_to_move
            except SQLAlchemyError as e:
                db.rollback()
                logger.error(f"Error moving item '{item_id}': {e}")
                raise exc.RepositoryError(f"Failed to move item '{item_id}': {e}")
            except exc.BaseAppException as e: # 사용자 정의 예외도 롤백
                db.rollback()
                logger.error(f"Application error moving item '{item_id}': {e}")
                raise 