import { Module } from '@nestjs/common';
import { TreeController } from './tree.controller';
import { TreeService } from './tree.service';

@Module({
    controllers: [TreeController],
    providers: [TreeService],
    exports: [TreeService]
})
export class TreeModule {} 