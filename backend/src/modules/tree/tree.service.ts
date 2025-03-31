import { Injectable } from '@nestjs/common';
import { ITreeState } from '../../../viewmodels/typescript/tree.interface';

@Injectable()
export class TreeService {
    private currentState: ITreeState = {
        nodes: {},
        structure: {},
        selectedItems: []
    };

    async getCurrentState(): Promise<ITreeState> {
        return this.currentState;
    }

    async updateState(state: ITreeState): Promise<void> {
        this.currentState = state;
    }

    async executeItem(id: string): Promise<boolean> {
        const item = this.currentState.nodes[id];
        if (!item) {
            return false;
        }

        // TODO: 실제 실행 로직 구현
        return true;
    }
} 