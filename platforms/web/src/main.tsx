import React from 'react';
import ReactDOM from 'react-dom/client';
import { TreeView } from './components/TreeView';
import { TreeViewModel } from '../../viewmodels/typescript/tree.viewmodel';
import { ItemViewModel } from '../../viewmodels/typescript/item.viewmodel';
import { TreeExecutor } from '../../viewmodels/typescript/tree.executor';

// ViewModel 인스턴스 생성
const treeViewModel = new TreeViewModel();
const itemViewModel = new ItemViewModel();
const treeExecutor = new TreeExecutor();

// React 컴포넌트에 ViewModel 주입
const App: React.FC = () => {
  return (
    <div className="app">
      <TreeView 
        treeViewModel={treeViewModel}
        itemViewModel={itemViewModel}
        treeExecutor={treeExecutor}
      />
    </div>
  );
};

// 앱 렌더링
const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
); 