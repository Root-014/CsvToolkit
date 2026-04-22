import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Filter, ArrowUp, ArrowDown, RotateCcw, FileText, Search } from 'lucide-react';
import MultiSelectDropdown from './MultiSelectDropdown';

const API_BASE = "http://localhost:8000";

const FileViewer = ({ 
  selectedFilePath, 
  setSelectedFilePath, 
  sheetData, 
  setSheetData, 
  sheetLoading, 
  setSheetLoading,
  sheetFilters,
  setSheetFilters,
  sheetSort,
  setSheetSort,
  sheetLimit,
  setSheetLimit
}) => {
  const [colValues, setColValues] = useState([]);        // unique values for filter col
  const [colValuesLoading, setColValuesLoading] = useState(false);

  
  const loadCsvData = async (path, options = {}) => {
    setSheetLoading(true);
    try {
      const currentVals = options.filter_vals !== undefined ? options.filter_vals : sheetFilters.vals;
      const res = await axios.post(`${API_BASE}/api/view_csv`, {
        file_path: path,
        filter_col: options.filter_col !== undefined ? options.filter_col : sheetFilters.col,
        filter_vals: currentVals,
        sort_col: options.sort_col !== undefined ? options.sort_col : sheetSort.col,
        sort_ascending: options.sort_ascending !== undefined ? options.sort_ascending : sheetSort.asc,
        limit_type: options.limit_type !== undefined ? options.limit_type : sheetLimit.type,
        limit_n: options.limit_n !== undefined ? options.limit_n : sheetLimit.n
      });
      if (res.data.status === 'success') {
        setSheetData(res.data);
      }
    } catch (err) {
      console.error("Failed to load CSV", err);
    } finally {
      setSheetLoading(false);
    }
  };

  // Fetch unique values for the selected filter column
  const fetchColumnValues = async (col) => {
    if (!col || !selectedFilePath) { setColValues([]); return; }
    setColValuesLoading(true);
    try {
      const res = await axios.post(`${API_BASE}/api/column_values`, {
        file_path: selectedFilePath,
        column: col
      });
      if (res.data.status === 'success') setColValues(res.data.values);
      else setColValues([]);
    } catch { setColValues([]); }
    finally { setColValuesLoading(false); }
  };

  useEffect(() => {
    if (selectedFilePath && selectedFilePath.endsWith('.csv')) {
      loadCsvData(selectedFilePath);
    } else {
      setSheetData(null);
    }
  }, [selectedFilePath]);

  const handleApplyOps = () => {
    loadCsvData(selectedFilePath);
  };

  const handleHeaderSort = (col) => {
    const newAsc = sheetSort.col === col ? !sheetSort.asc : true;
    setSheetSort({ col, asc: newAsc });
    loadCsvData(selectedFilePath, { 
      sort_col: col, 
      sort_ascending: newAsc 
    });
  };

  const resetOps = () => {
    const defaultFilters = { col: "", vals: [] };
    const defaultSort = { col: "", asc: true };
    const defaultLimit = { type: "top", n: 50 };
    setSheetFilters(defaultFilters);
    setSheetSort(defaultSort);
    setSheetLimit(defaultLimit);
    setColValues([]);
    loadCsvData(selectedFilePath, {
      filter_col: "",
      filter_vals: [],
      sort_col: "",
      sort_ascending: true,
      limit_type: "top",
      limit_n: 50
    });
  };

  return (
    <div className="file-viewer-container">
      <div className="sheets-view">
        {selectedFilePath ? (
          selectedFilePath.endsWith('.csv') ? (
            <>
              <div className="sheets-toolbar">
                <div className="toolbar-group">
                   <span className="toolbar-label"><Filter size={14}/> Filter:</span>
                   <select
                     className="sheets-select"
                     value={sheetFilters.col}
                     onChange={(e) => {
                       const newCol = e.target.value;
                       setSheetFilters({ col: newCol, vals: [] });
                       fetchColumnValues(newCol);
                     }}
                   >
                     <option value="">Select Column</option>
                     {sheetData?.columns.map(c => <option key={c} value={c}>{c}</option>)}
                   </select>
                   <MultiSelectDropdown
                     options={colValues}
                     selected={sheetFilters.vals || []}
                     onChange={(vals) => setSheetFilters(f => ({ ...f, vals }))}
                     disabled={!sheetFilters.col || colValuesLoading}
                     placeholder={colValuesLoading ? 'Loading...' : 'Select values...'}
                   />
                </div>

                <div className="toolbar-group">
                   <span className="toolbar-label"><ArrowUp size={14}/> Sort:</span>
                   <select 
                     className="sheets-select"
                     value={sheetSort.col}
                     onChange={(e) => setSheetSort({...sheetSort, col: e.target.value})}
                   >
                     <option value="">Select Column</option>
                     {sheetData?.columns.map(c => <option key={c} value={c}>{c}</option>)}
                   </select>
                   <button 
                     className="terminal-btn"
                     onClick={() => setSheetSort({...sheetSort, asc: !sheetSort.asc})}
                   >
                     {sheetSort.asc ? <ArrowUp size={14}/> : <ArrowDown size={14}/>}
                   </button>
                </div>

                <div className="toolbar-group">
                   <select 
                     className="sheets-select"
                     value={sheetLimit.type}
                     onChange={(e) => setSheetLimit({...sheetLimit, type: e.target.value})}
                   >
                     <option value="top">Top</option>
                     <option value="bottom">Bottom</option>
                   </select>
                   <input 
                     type="number"
                     className="sheets-input"
                     style={{ width: '60px' }}
                     value={sheetLimit.n}
                     onChange={(e) => setSheetLimit({...sheetLimit, n: parseInt(e.target.value) || 10})}
                   />
                </div>

                <div className="toolbar-group" style={{marginLeft: 'auto'}}>
                   <button className="btn-primary" style={{padding: '6px 12px', fontSize: '0.85rem'}} onClick={handleApplyOps}>
                      Apply
                   </button>
                   <button className="terminal-btn" title="Reset" onClick={resetOps}>
                      <RotateCcw size={14} />
                   </button>
                </div>
              </div>

              <div className="sheets-table-container">
                {sheetLoading ? (
                  <div className="sheets-empty">
                    <div className="spinner"></div>
                    <span>Processing with Pandas...</span>
                  </div>
                ) : sheetData ? (
                  <table className="sheets-table">
                    <thead>
                      <tr>
                        {sheetData.columns.map(col => (
                          <th key={col} onClick={() => handleHeaderSort(col)} className="sortable-header">
                            <div className="header-content">
                              {col}
                              {sheetSort.col === col && (
                                <span className="sort-icon">
                                  {sheetSort.asc ? <ArrowUp size={12}/> : <ArrowDown size={12}/>}
                                </span>
                              )}
                            </div>
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {sheetData.data.map((row, i) => (
                        <tr key={i}>
                          {sheetData.columns.map(col => (
                            <td key={col}>{String(row[col] ?? '')}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                ) : null}
              </div>

              <div className="sheets-status">
                 {sheetData && (
                   <>
                     <span>Showing {sheetData.display_rows} of {sheetData.total_rows} rows</span>
                     <span>{selectedFilePath}</span>
                   </>
                 )}
              </div>
            </>
          ) : selectedFilePath.toLowerCase().endsWith('.html') ? (
            <div className="sheets-html-viewer" style={{ display: 'flex', flexDirection: 'column', height: '100%', width: '100%' }}>
              <div style={{ display: 'flex', justifyContent: 'flex-end', padding: '8px', borderBottom: '1px solid var(--glass-border)' }}>
                 <button 
                   className="btn-primary" 
                   onClick={() => window.open(`${API_BASE}/api/file_content?path=${encodeURIComponent(selectedFilePath)}`, '_blank')}
                 >
                   Open in New Tab
                 </button>
              </div>
              <iframe 
                src={`${API_BASE}/api/file_content?path=${encodeURIComponent(selectedFilePath)}`} 
                style={{ flex: 1, border: 'none', backgroundColor: 'white', borderRadius: '0 0 8px 8px' }} 
                title="HTML Viewer"
              />
            </div>
          ) : (
            <div className="sheets-empty">
               <FileText size={48} style={{ opacity: 0.2 }} />
               <span>Click a CSV or HTML file on the left to view data.</span>
            </div>
          )
        ) : (
          <div className="sheets-empty">
             <Search size={48} style={{ opacity: 0.2 }} />
             <span>Select a file to begin explorer.</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default FileViewer;
