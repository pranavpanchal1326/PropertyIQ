import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronDown, Loader2 } from 'lucide-react'

const CITIES = [
  'Mumbai','Delhi','Bengaluru','Hyderabad',
  'Pune','Chennai','Kolkata','Ahmedabad',
  'Gurgaon','Navi Mumbai',
]

// ── Reusable label ─────────────────────────────────────────────────────────
function FieldLabel({ children }) {
  return (
    <div style={{
      fontSize:      11,
      fontWeight:    600,
      color:         '#656D76',
      marginBottom:  6,
      textTransform: 'uppercase',
      letterSpacing: '0.5px',
    }}>
      {children}
    </div>
  )
}

// ── Select dropdown ────────────────────────────────────────────────────────
function SelectField({ value, onChange, options, placeholder }) {
  return (
    <div style={{ position: 'relative' }}>
      <select
        value={value}
        onChange={e => onChange(e.target.value)}
        style={{
          width:        '100%',
          height:       42,
          background:   '#FFFFFF',
          border:       '1px solid #D0D7DE',
          borderRadius: 6,
          padding:      '0 36px 0 14px',
          fontSize:     14,
          fontWeight:   500,
          color:        value ? '#1F2328' : '#8C959F',
          appearance:   'none',
          cursor:       'pointer',
          outline:      'none',
          fontFamily:   'inherit',
          transition:   'border-color 0.15s',
        }}
        onFocus={e  => e.target.style.borderColor = '#0D9488'}
        onBlur={e   => e.target.style.borderColor = '#D0D7DE'}
      >
        {placeholder && (
          <option value="" disabled>{placeholder}</option>
        )}
        {options.map(o => (
          <option key={o} value={o}>{o}</option>
        ))}
      </select>
      <ChevronDown
        size={14}
        color="#8C959F"
        strokeWidth={1.5}
        style={{
          position:      'absolute',
          right:         12,
          top:           '50%',
          transform:     'translateY(-50%)',
          pointerEvents: 'none',
        }}
      />
    </div>
  )
}

// ── Segmented control ──────────────────────────────────────────────────────
function SegmentedControl({ value, onChange, options }) {
  return (
    <div style={{
      display:      'flex',
      background:   '#EAEEF2',
      borderRadius: 8,
      padding:      3,
      gap:          2,
    }}>
      {options.map(opt => {
        const active = value === opt.value
        return (
          <motion.button
            key={opt.value}
            onClick={() => onChange(opt.value)}
            whileTap={{ scale: 0.97 }}
            style={{
              flex:         1,
              height:       36,
              borderRadius: 6,
              background:   active ? '#FFFFFF' : 'transparent',
              border:       'none',
              cursor:       'pointer',
              fontSize:     13,
              fontWeight:   active ? 700 : 500,
              color:        active ? '#1F2328' : '#656D76',
              fontFamily:   'inherit',
              boxShadow:    active
                ? '0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.06)'
                : 'none',
              transition:   'all 0.15s',
            }}
          >
            {opt.label}
          </motion.button>
        )
      })}
    </div>
  )
}

// ── Stepper ────────────────────────────────────────────────────────────────
function Stepper({ value, onChange, min = 1, max = 8 }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center' }}>
      <button
        onClick={() => onChange(Math.max(min, value - 1))}
        style={{
          width:        36,
          height:       42,
          background:   '#FFFFFF',
          border:       '1px solid #D0D7DE',
          borderRadius: '6px 0 0 6px',
          cursor:       value <= min ? 'not-allowed' : 'pointer',
          fontSize:     18,
          color:        value <= min ? '#D0D7DE' : '#656D76',
          fontFamily:   'inherit',
          display:      'flex',
          alignItems:   'center',
          justifyContent: 'center',
          transition:   'color 0.15s',
        }}
      >
        −
      </button>
      <div style={{
        width:        52,
        height:       42,
        background:   '#FFFFFF',
        borderTop:    '1px solid #D0D7DE',
        borderBottom: '1px solid #D0D7DE',
        display:      'flex',
        alignItems:   'center',
        justifyContent: 'center',
        fontSize:     14,
        fontWeight:   700,
        color:        '#1F2328',
      }}>
        {value}
      </div>
      <button
        onClick={() => onChange(Math.min(max, value + 1))}
        style={{
          width:        36,
          height:       42,
          background:   '#FFFFFF',
          border:       '1px solid #D0D7DE',
          borderRadius: '0 6px 6px 0',
          cursor:       value >= max ? 'not-allowed' : 'pointer',
          fontSize:     18,
          color:        value >= max ? '#D0D7DE' : '#656D76',
          fontFamily:   'inherit',
          display:      'flex',
          alignItems:   'center',
          justifyContent: 'center',
          transition:   'color 0.15s',
        }}
      >
        +
      </button>
    </div>
  )
}

// ── Main form ──────────────────────────────────────────────────────────────
export default function ValuationForm({ localities, onSubmit, loading, onCityChange }) {
  const [form, setForm] = useState({
    city:          'Mumbai',
    locality:      '',
    bhk:           3,
    total_sqft:    1200,
    bath:          3,
    property_type: 'Apartment',
    furnishing:    'Semi-Furnished',
  })
  
  const set = (key, val) => setForm(f => ({ ...f, [key]: val }))
  
  const canSubmit = form.locality !== '' && !loading
  
  function handleSubmit() {
    if (!canSubmit) return
    onSubmit({ ...form })
  }
  
  return (
    <div>
      {/* Section label */}
      <div style={{
        fontSize:      10,
        fontWeight:    600,
        color:         '#94A3B8',
        textTransform: 'uppercase',
        letterSpacing: '2px',
        marginBottom:  24,
      }}>
        Property Details
      </div>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
        
        {/* City */}
        <div>
          <FieldLabel>City</FieldLabel>
          <SelectField
            value={form.city}
            onChange={v => {
              set('city', v)
              set('locality', '')
              if (onCityChange) onCityChange(v)
            }}
            options={CITIES}
          />
        </div>
        
        {/* Locality */}
        <div>
          <FieldLabel>Locality</FieldLabel>
          <SelectField
            value={form.locality}
            onChange={v => set('locality', v)}
            options={localities}
            placeholder="Select locality..."
          />
          {!form.locality && (
            <div style={{
              fontSize:  10,
              color:     '#94A3B8',
              marginTop: 4,
            }}>
              Select a locality to enable valuation
            </div>
          )}
        </div>
        
        {/* BHK */}
        <div>
          <FieldLabel>BHK Configuration</FieldLabel>
          <SegmentedControl
            value={form.bhk}
            onChange={v => set('bhk', v)}
            options={[
              { value: 1, label: '1' },
              { value: 2, label: '2' },
              { value: 3, label: '3' },
              { value: 4, label: '4' },
              { value: 5, label: '4+' },
            ]}
          />
        </div>
        
        {/* Total area */}
        <div>
          <FieldLabel>Total Area</FieldLabel>
          <div style={{ position: 'relative' }}>
            <input
              type="number"
              value={form.total_sqft}
              min={200}
              max={10000}
              onChange={e => set('total_sqft', parseFloat(e.target.value) || 0)}
              style={{
                width:        '100%',
                height:       42,
                background:   '#FFFFFF',
                border:       '1px solid #D0D7DE',
                borderRadius: 6,
                padding:      '0 48px 0 14px',
                fontSize:     14,
                fontWeight:   500,
                color:        '#1F2328',
                outline:      'none',
                fontFamily:   'inherit',
                transition:   'border-color 0.15s',
              }}
              onFocus={e => e.target.style.borderColor = '#0D9488'}
              onBlur={e  => e.target.style.borderColor = '#D0D7DE'}
            />
            <span style={{
              position:      'absolute',
              right:         14,
              top:           '50%',
              transform:     'translateY(-50%)',
              fontSize:      12,
              color:         '#8C959F',
              pointerEvents: 'none',
            }}>
              sqft
            </span>
          </div>
        </div>
        
        {/* Bathrooms */}
        <div>
          <FieldLabel>Bathrooms</FieldLabel>
          <Stepper
            value={form.bath}
            onChange={v => set('bath', v)}
            min={1}
            max={form.bhk + 2}
          />
        </div>
        
        {/* Property type */}
        <div>
          <FieldLabel>Property Type</FieldLabel>
          <SegmentedControl
            value={form.property_type}
            onChange={v => set('property_type', v)}
            options={[
              { value: 'Apartment',   label: 'Apartment'   },
              { value: 'Villa',       label: 'Villa'        },
              { value: 'Independent', label: 'Independent' },
            ]}
          />
        </div>
        
        {/* Furnishing */}
        <div>
          <FieldLabel>Furnishing</FieldLabel>
          <SegmentedControl
            value={form.furnishing}
            onChange={v => set('furnishing', v)}
            options={[
              { value: 'Unfurnished',    label: 'Unfurnished' },
              { value: 'Semi-Furnished', label: 'Semi'        },
              { value: 'Fully Furnished',label: 'Furnished'   },
            ]}
          />
        </div>
        
        {/* Submit button */}
        <motion.button
          onClick={handleSubmit}
          disabled={!canSubmit}
          whileHover={canSubmit ? { scale: 1.01 } : {}}
          whileTap={canSubmit  ? { scale: 0.97 } : {}}
          style={{
            width:        '100%',
            height:       52,
            background:   canSubmit ? '#0D9488' : '#EAEEF2',
            border:       'none',
            borderRadius: 8,
            fontSize:     15,
            fontWeight:   700,
            color:        canSubmit ? '#FFFFFF' : '#8C959F',
            cursor:       canSubmit ? 'pointer' : 'not-allowed',
            display:      'flex',
            alignItems:   'center',
            justifyContent: 'center',
            gap:          8,
            fontFamily:   'inherit',
            marginTop:    8,
            boxShadow:    canSubmit
              ? 'inset 0 1px 0 rgba(255,255,255,0.15)'
              : 'none',
            transition:   'background 0.2s, color 0.2s',
          }}
        >
          <AnimatePresence mode="wait">
            {loading ? (
              <motion.div
                key="loading"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{  opacity: 0 }}
                style={{ display: 'flex', alignItems: 'center', gap: 8 }}
              >
                <Loader2
                  size={18}
                  strokeWidth={2}
                  style={{ animation: 'spin 0.8s linear infinite' }}
                />
                Calculating...
              </motion.div>
            ) : (
              <motion.div
                key="idle"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{  opacity: 0 }}
                style={{ display: 'flex', alignItems: 'center', gap: 8 }}
              >
                Get Valuation →
              </motion.div>
            )}
          </AnimatePresence>
        </motion.button>
       </div>
    </div>
  )
}
