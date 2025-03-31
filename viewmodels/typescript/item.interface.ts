import { ITreeItem } from './tree.interface';

export interface IItemViewModel {
    id: string;
    name: string;
    type: 'group' | 'inst';
    inputType?: 'mouse' | 'keyboard';
    subAction?: string;
    subContent?: string;
    
    isGroup(): boolean;
    isInst(): boolean;
    getChildren(): IItemViewModel[];
    setChildren(children: IItemViewModel[]): void;
    addChild(child: IItemViewModel): void;
    removeChild(childId: string): void;
    update(updates: Partial<ITreeItem>): void;
} 