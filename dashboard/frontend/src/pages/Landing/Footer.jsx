export default function Footer() {
  return (
    <footer style={{
      background:   '#06090F',
      borderTop:    '1px solid #21262D',
      padding:      '40px 80px',
    }}>
      <div style={{
        display:        'flex',
        justifyContent: 'space-between',
        alignItems:     'center',
        marginBottom:   16,
      }}>
        {/* Logo */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div style={{ position: 'relative', width: 18, height: 18 }}>
            <div style={{
              width: 11, height: 11, background: '#2DD4BF',
              borderRadius: 2, position: 'absolute', top: 0, left: 0,
            }} />
            <div style={{
              width: 11, height: 11, background: '#2DD4BF',
              borderRadius: 2, position: 'absolute', bottom: 0, right: 0,
              opacity: 0.4,
            }} />
          </div>
          <span style={{ fontSize: 14, fontWeight: 700, color: '#E6EDF3' }}>
            PropertyIQ
          </span>
        </div>
        
        {/* Nav links */}
        <div style={{ display: 'flex', gap: 32 }}>
          {['Product','Data','Methodology','API Docs'].map(l => (
            <span key={l} style={{ fontSize: 13, color: '#484F58', cursor: 'pointer' }}>
              {l}
            </span>
          ))}
        </div>
        
        {/* Right label */}
        <span style={{ fontSize: 12, color: '#484F58' }}>
          DSBDA Capstone 2026
        </span>
      </div>
      
      <div style={{
        textAlign: 'center',
        fontSize:  12,
        color:     '#30363D',
        lineHeight: 1.6,
      }}>
        Built on 600,000 Indian property observations · Python 3.13 · scikit-learn · FastAPI · React
        {' '}·{' '}
        RBI MRM Circular 2023 Alignment
      </div>
    </footer>
  )
}
