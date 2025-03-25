export interface ITreeItem {
    id: string;
    name: string;
    type: 'group' | 'inst';
    inputType?: 'mouse' | 'keyboard';
    subAction?: string;
    subContent?: string;
    children?: ITreeItem[];
}

export interface ITreeViewModel {
    getCurrentState(): ITreeState;
    restoreState(state: ITreeState): void;
    getSelectedItems(): string[];
    selectItem(itemId: string): void;
    deselectItem(itemId: string): void;
    addItem(parentId: string | null, item: ITreeItem): void;
    removeItem(itemId: string): void;
    updateItem(itemId: string, updates: Partial<ITreeItem>): void;
}

export interface ITreeState {
    nodes: { [key: string]: ITreeItem };
    structure: { [key: string | null]: string[] };
    selectedItems: string[];
} 