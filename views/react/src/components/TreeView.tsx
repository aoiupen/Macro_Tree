import React from 'react';
import { ITreeItem } from '../../../viewmodels/typescript/tree.interface';

interface TreeViewProps {
    items: ITreeItem[];
    onItemSelect: (itemId: string) => void;
    selectedItems: string[];
}

export const TreeView: React.FC<TreeViewProps> = ({ items, onItemSelect, selectedItems }) => {
    const renderItem = (item: ITreeItem, level: number = 0) => {
        const isSelected = selectedItems.includes(item.id);
        const paddingLeft = `${level * 20}px`;

        return (
            <div key={item.id} style={{ paddingLeft }}>
                <div
                    className={`tree-item ${isSelected ? 'selected' : ''}`}
                    onClick={() => onItemSelect(item.id)}
                >
                    <span className="item-icon">
                        {item.type === 'group' ? '📁' : '📄'}
                    </span>
                    <span className="item-name">{item.name}</span>
                    {item.inputType && (
                        <span className="item-type">
                            {item.inputType === 'mouse' ? '🖱️' : '⌨️'}
                        </span>
                    )}
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