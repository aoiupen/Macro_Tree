import React, { useEffect, useState } from 'react';
import { TreeViewModel } from '../../../viewmodels/typescript/tree.viewmodel';
import { ItemViewModel } from '../../../viewmodels/typescript/item.viewmodel';
import { TreeExecutor } from '../../../viewmodels/typescript/tree.executor';
import { ITreeItem } from '../../../viewmodels/typescript/tree.interface';

interface TreeViewProps {
  treeViewModel: TreeViewModel;
  itemViewModel: ItemViewModel;
  treeExecutor: TreeExecutor;
}

export const TreeView: React.FC<TreeViewProps> = ({
  treeViewModel,
  itemViewModel,
  treeExecutor
}) => {
  const [items, setItems] = useState<ITreeItem[]>([]);
  const [selectedItems, setSelectedItems] = useState<string[]>([]);

  useEffect(() => {
    // 초기 데이터 로드
    const loadItems = async () => {
      const treeItems = await treeViewModel.get_items();
      setItems(treeItems);
    };
    loadItems();

    // 이벤트 리스너 등록
    const handleItemSelect = (itemId: string) => {
      setSelectedItems(prev => [...prev, itemId]);
    };

    const handleItemExecute = async (itemId: string) => {
      await treeExecutor.execute_item(itemId);
    };

    // 이벤트 리스너 등록
    treeViewModel.on('itemSelected', handleItemSelect);
    treeViewModel.on('itemExecuted', handleItemExecute);

    // 클린업
    return () => {
      treeViewModel.off('itemSelected', handleItemSelect);
      treeViewModel.off('itemExecuted', handleItemExecute);
    };
  }, [treeViewModel, treeExecutor]);

  const renderItem = (item: ITreeItem, level: number = 0) => {
    const isSelected = selectedItems.includes(item.id);
    const isGroup = itemViewModel.is_group(item.id);
    const isInst = itemViewModel.is_inst(item.id);

    return (
      <div key={item.id} style={{ marginLeft: `${level * 20}px` }}>
        <div
          className={`tree-item ${isSelected ? 'selected' : ''}`}
          onClick={() => treeViewModel.select_item(item.id)}
        >
          <span className="item-icon">
            {isGroup ? '📁' : isInst ? '⚙️' : '📄'}
          </span>
          <span className="item-name">{item.name}</span>
        </div>
        {item.children && item.children.map(child => renderItem(child, level + 1))}
      </div>
    );
  };

  return (
    <div className="tree-view">
      {items.map(item => renderItem(item))}
    </div>
  );
}; 