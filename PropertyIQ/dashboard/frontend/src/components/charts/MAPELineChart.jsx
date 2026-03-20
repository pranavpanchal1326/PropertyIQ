import { useRef, useMemo } from 'react'
import { motion, useInView } from 'framer-motion'
import {
  AreaChart, Area, XAxis, YAxis,
  ReferenceLine, ResponsiveContainer,
  Tooltip,
} from 'recharts'

// ── Custom tooltip ─────────────────────────────────────────────────────────
function MAPETooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  const val     = payload[0]?.value
  const isAlert = val > 20
  
  return (
    <div style={{
      background:   'var(--bg-overlay)',
      border:       '1px solid var(--border-muted)',
      borderRadius: 6,
      padding:      '8px 12px',
      pointerEvents: 'none',
    }}>
      <div style={{
        fontSize: 10,
        color:    'var(--text-ghost)',
        marginBottom: 4,
      }}>
        Window {label}
      </div>
      <div style={{
        fontSize:   13,
        fontWeight: 700,
        color:      isAlert ? 'var(--red)' : 'var(--teal)',
      }}>
        {val?.toFixed(2)}%
      </div>
      {isAlert && (
        <div style={{
          fontSize:   9,
          color:      'var(--red)',
          marginTop:  3,
        }}>
          ⚠ Above alert threshold
        </div>
      )}
    </div>
  )
}

export default function MAPELineChart({ data }) {
  const ref    = useRef(null)
  const inView = useInView(ref, { once: true, margin: '0px 0px -40px 0px' })
  
  // Transform API data to recharts format
  const chartData = useMemo(() => {
    if (!data?.windows) return []
    return data.windows.map(w => ({
      window: w.window_idx,
      mape:   parseFloat(w.window_mape.toFixed(3)),
      alert:  w.alert,
    }))
  }, [data])
  
  if (!chartData.length) return null
  
  return (
    <div
      ref={ref}
      style={{
        background:   'var(--bg-base)',
        border:       '1px solid var(--border-subtle)',
        borderRadius: 8,
        padding:      20,
      }}
    >
      {/* Header */}
      <div style={{ marginBottom: 4 }}>
        <span style={{
          fontSize:   13,
          fontWeight: 700,
          color:      'var(--text-primary)',
        }}>
          Rolling MAPE — 600 Windows
        </span>
      </div>
      <div style={{
        fontSize:     11,
        color:        'var(--text-secondary)',
        marginBottom: 20,
      }}>
        500-row windows · 2025 drift dataset · baseline 1.61%
      </div>
      
      {/* Chart */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={inView ? { opacity: 1 } : { opacity: 0 }}
        transition={{ duration: 0.4 }}
        style={{ height: 200 }}
      >
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart
            data={chartData}
            margin={{ top: 8, right: 16, bottom: 0, left: -16 }}
          >
            <defs>
              {/* Teal gradient fill under line */}
              <linearGradient id="mapeGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%"  stopColor="#2DD4BF" stopOpacity={0.15} />
                <stop offset="95%" stopColor="#2DD4BF" stopOpacity={0}    />
              </linearGradient>
              {/* Red gradient for alert region */}
              <linearGradient id="alertGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%"   stopColor="#FF7B72" stopOpacity={0.08} />
                <stop offset="100%" stopColor="#FF7B72" stopOpacity={0}    />
              </linearGradient>
            </defs>
            
            <XAxis
              dataKey="window"
              ticks={[1, 100, 200, 300, 400, 500, 600]}
              tick={{ fontSize: 10, fill: 'var(--text-ghost)', fontFamily: 'inherit' }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              tickFormatter={v => `${v}%`}
              tick={{ fontSize: 10, fill: 'var(--text-ghost)', fontFamily: 'inherit' }}
              axisLine={false}
              tickLine={false}
              domain={[0, 45]}
              ticks={[0, 10, 20, 30, 40]}
            />
            <Tooltip
              content={<MAPETooltip />}
              cursor={{ stroke: 'var(--border-muted)', strokeWidth: 1 }}
            />
            
            {/* Alert threshold reference line */}
            <ReferenceLine
              y={20}
              stroke="var(--red)"
              strokeDasharray="4 3"
              strokeWidth={1}
              label={{
                value:    'Alert 20%',
                position: 'insideTopRight',
                fontSize: 9,
                fill:     'var(--red)',
                fontFamily: 'inherit',
              }}
            />
            
            {/* Main MAPE area */}
            <Area
              type="monotone"
              dataKey="mape"
              stroke="var(--teal)"
              strokeWidth={1.5}
              fill="url(#mapeGradient)"
              dot={false}
              activeDot={{
                r:           4,
                fill:        'var(--teal)',
                strokeWidth: 0,
              }}
              isAnimationActive={inView}
              animationDuration={1600}
              animationEasing="ease-in-out"
            />
          </AreaChart>
        </ResponsiveContainer>
      </motion.div>
      
      {/* Spike annotation */}
      <motion.div
        initial={{ opacity: 0, y: 4 }}
        animate={inView ? { opacity: 1, y: 0 } : { opacity: 0 }}
        transition={{ delay: 1.0, duration: 0.3 }}
        style={{
          marginTop:    12,
          display:      'inline-flex',
          alignItems:   'center',
          gap:          8,
          background:   'var(--bg-overlay)',
          border:       '1px solid var(--border-muted)',
          borderRadius: 6,
          padding:      '6px 12px',
        }}
      >
        <div style={{
          width:        7,
          height:       7,
          borderRadius: '50%',
          background:   'var(--red)',
          flexShrink:   0,
        }} />
        <span style={{
          fontSize:   11,
          fontWeight: 600,
          color:      'var(--text-primary)',
        }}>
          Ultra-premium tail
        </span>
        <span style={{
          fontSize: 11,
          color:    'var(--text-secondary)',
        }}>
          Windows 589–600 · top 2% of properties · peak 40.8%
        </span>
      </motion.div>
    </div>
  )
}
