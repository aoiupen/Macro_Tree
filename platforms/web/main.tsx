import React from 'react';
import ReactDOM from 'react-dom/client';
import { TreeView } from './components/TreeView';
import './index.css';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <TreeView 
      items={[]} 
      onItemSelect={() => {}} 
      selectedItems={[]} 
    />
  </React.StrictMode>
); 