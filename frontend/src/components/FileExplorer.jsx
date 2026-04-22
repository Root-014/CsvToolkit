import React, { useEffect } from 'react';
import axios from 'axios';
import { Folder, FileText } from 'lucide-react';

const API_BASE = "http://localhost:8000";

const FileExplorer = ({ exploreFiles, selectedFilePath, setSelectedFilePath, setExploreFiles }) => {
  const fetchFiles = async () => {
    try {
      const res = await axios.get(`${API_BASE}/api/files`);
      if (res.data.status === 'success') {
        setExploreFiles(res.data.files);
      }
    } catch (err) {
      console.error("Failed to fetch files", err);
    }
  };

  useEffect(() => {
    fetchFiles();
  }, []);

  const renderTree = (items) => {
    return items.map(item => (
      <div key={item.path} style={{ marginLeft: item.isDir ? '0' : '12px' }}>
        <div 
          className={`tree-item ${item.isDir ? 'folder' : 'file'} ${selectedFilePath === item.path ? 'active' : ''}`}
          onClick={() => !item.isDir && setSelectedFilePath(item.path)}
        >
          {item.isDir ? <Folder size={14} /> : <FileText size={14} />}
          <span>{item.name}</span>
        </div>
        {item.isDir && item.children && item.children.length > 0 && (
          <div style={{ marginLeft: '16px', borderLeft: '1px solid var(--glass-border)' }}>
            {renderTree(item.children)}
          </div>
        )}
      </div>
    ));
  };

  return (
    <div className="file-explorer">
      <div className="explorer-header">
         <Folder size={16} /> PROJECT FILES
      </div>
      <div className="explorer-tree">
         {renderTree(exploreFiles)}
      </div>
    </div>
  );
};

export default FileExplorer;
