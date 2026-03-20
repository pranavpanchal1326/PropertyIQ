/**
 * Skeleton loading state for a KPI stat card.
 * Matches exact dimensions of StatCard component.
 */
export function SkeletonStatCard() {
  return (
    <div style={{
      background:   'var(--bg-base)',
      border:       '1px solid var(--border-subtle)',
      borderRadius: 8,
      padding:      '20px 24px',
      height:       96,
    }}>
      {/* Icon + label row */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14 }}>
        <div className="skeleton" style={{ width: 32, height: 32, borderRadius: '50%' }} />
        <div className="skeleton" style={{ width: 110, height: 10 }} />
      </div>
      {/* Value */}
      <div className="skeleton" style={{ width: 72, height: 28, marginBottom: 8 }} />
      {/* Sub */}
      <div className="skeleton" style={{ width: 160, height: 9 }} />
    </div>
  )
}

/**
 * Skeleton loading state for a chart card.
 * @param {number} height - Chart area height in px (default 280)
 */
export function SkeletonChart({ height = 280 }) {
  return (
    <div style={{
      background:   'var(--bg-base)',
      border:       '1px solid var(--border-subtle)',
      borderRadius: 8,
      padding:      20,
    }}>
      {/* Title */}
      <div className="skeleton" style={{ width: 200, height: 13, marginBottom: 8 }} />
      {/* Subtitle */}
      <div className="skeleton" style={{ width: 280, height: 10, marginBottom: 24 }} />
      {/* Chart area */}
      <div className="skeleton" style={{ width: '100%', height }} />
    </div>
  )
}

/**
 * Skeleton loading state for a single table row.
 * Stack multiple to simulate a loading table.
 */
export function SkeletonRow() {
  return (
    <div style={{
      display:       'flex',
      alignItems:    'center',
      gap:           16,
      padding:       '14px 24px',
      borderBottom:  '1px solid var(--border-subtle)',
    }}>
      <div className="skeleton" style={{ width: 24, height: 24, borderRadius: '50%', flexShrink: 0 }} />
      <div className="skeleton" style={{ width: 120, height: 11 }} />
      <div style={{ flex: 1 }} />
      <div className="skeleton" style={{ width: 60, height: 11 }} />
      <div className="skeleton" style={{ width: 80, height: 11 }} />
      <div className="skeleton" style={{ width: 50, height: 24, borderRadius: 4 }} />
    </div>
  )
}

/**
 * Skeleton for the full city drift table
 * including header + 5 rows
 */
export function SkeletonTable() {
  return (
    <div style={{
      background:   'var(--bg-base)',
      border:       '1px solid var(--border-subtle)',
      borderRadius: 8,
      overflow:     'hidden',
    }}>
      {/* Table header */}
      <div style={{
        padding:      '14px 24px',
        borderBottom: '1px solid var(--border-subtle)',
        display:      'flex',
        alignItems:   'center',
        justifyContent: 'space-between',
      }}>
        <div>
          <div className="skeleton" style={{ width: 160, height: 13, marginBottom: 6 }} />
          <div className="skeleton" style={{ width: 200, height: 10 }} />
        </div>
        <div className="skeleton" style={{ width: 180, height: 34, borderRadius: 6 }} />
      </div>
      {/* Column headers */}
      <div style={{
        padding:      '10px 24px',
        borderBottom: '1px solid var(--border-subtle)',
        display:      'flex', gap: 16,
      }}>
        {[56, 160, 100, 140, 80].map((w, i) => (
          <div key={i} className="skeleton" style={{ width: w, height: 9 }} />
        ))}
      </div>
      {/* Rows */}
      {Array(5).fill(0).map((_, i) => <SkeletonRow key={i} />)}
    </div>
  )
}
