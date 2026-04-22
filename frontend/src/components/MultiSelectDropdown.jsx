import React, { useState, useRef, useEffect } from 'react';
import { ChevronDown, Search } from 'lucide-react';

const MultiSelectDropdown = ({ options, selected, onChange, disabled, placeholder }) => {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState('');
  const ref = useRef(null);

  // Close when clicking outside
  useEffect(() => {
    const handler = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false); };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const filtered = options.filter(o => o.toLowerCase().includes(search.toLowerCase()));

  const toggle = (val) => {
    if (selected.includes(val)) onChange(selected.filter(v => v !== val));
    else onChange([...selected, val]);
  };

  const selectAll = () => onChange(filtered);
  const clearAll  = () => onChange([]);

  const label = selected.length === 0
    ? (placeholder || 'Select values...')
    : selected.length === 1
      ? selected[0]
      : `${selected.length} selected`;

  return (
    <div className="ms-dropdown" ref={ref}>
      <button
        className={`ms-trigger ${open ? 'open' : ''} ${disabled ? 'disabled' : ''}`}
        onClick={() => !disabled && setOpen(o => !o)}
        type="button"
      >
        <span className="ms-label">{label}</span>
        <ChevronDown size={12} className={`ms-chevron ${open ? 'rotated' : ''}`} />
      </button>

      {open && (
        <div className="ms-panel">
          {/* Search */}
          <div className="ms-search-wrap">
            <Search size={13} className="ms-search-icon" />
            <input
              className="ms-search"
              placeholder="Search..."
              value={search}
              onChange={e => setSearch(e.target.value)}
              autoFocus
            />
          </div>

          {/* Bulk actions */}
          <div className="ms-bulk">
            <button className="ms-bulk-btn" onClick={selectAll}>All</button>
            <button className="ms-bulk-btn" onClick={clearAll}>None</button>
            <span className="ms-count">{selected.length}/{options.length}</span>
          </div>

          {/* Options list */}
          <div className="ms-options">
            {filtered.length === 0
              ? <div className="ms-empty">No matches</div>
              : filtered.map(opt => (
                <label key={opt} className="ms-option">
                  <input
                    type="checkbox"
                    checked={selected.includes(opt)}
                    onChange={() => toggle(opt)}
                  />
                  <span>{opt}</span>
                </label>
              ))
            }
          </div>
        </div>
      )}
    </div>
  );
};

export default MultiSelectDropdown;
