import { IPlatform, IPlatformConfig } from '../common/platform_interface';

export class WebPlatformConfig implements IPlatformConfig {
    getPlatformName(): string {
        return "web";
    }

    getPlatformVersion(): string {
        return "1.0.0";
    }

    getPlatformSettings(): Record<string, any> {
        return {
            title: "Macro Tree Web",
            theme: "light",
            apiEndpoint: "/api"
        };
    }
}

export class WebPlatform implements IPlatform {
    private config: WebPlatformConfig;
    private rootElement: HTMLElement | null = null;

    constructor(config: WebPlatformConfig) {
        this.config = config;
    }

    initialize(): void {
        // React 앱 초기화
        this.rootElement = document.getElementById('root');
        if (!this.rootElement) {
            throw new Error('Root element not found');
        }
    }

    createWindow(title: string): HTMLElement {
        // 웹에서는 document.title 사용
        document.title = title;
        return this.rootElement!;
    }

    run(): void {
        // React 앱 렌더링
        // 실제 구현은 React 컴포넌트에서 처리
    }
} 