import { Controller, Get, Post, Body, Param } from '@nestjs/common';
import { TreeService } from './tree.service';
import { ITreeState } from '../../../viewmodels/typescript/tree.interface';

@Controller('tree')
export class TreeController {
    constructor(private readonly treeService: TreeService) {}

    @Get()
    async getTreeState(): Promise<ITreeState> {
        return this.treeService.getCurrentState();
    }

    @Post()
    async updateTreeState(@Body() state: ITreeState): Promise<void> {
        await this.treeService.updateState(state);
    }

    @Post(':id/execute')
    async executeItem(@Param('id') id: string): Promise<boolean> {
        return this.treeService.executeItem(id);
    }
} 