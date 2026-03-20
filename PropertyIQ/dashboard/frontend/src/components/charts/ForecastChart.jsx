import { useMemo } from 'react'
import {
  AreaChart, Area, XAxis, YAxis,
  ResponsiveContainer, Tooltip,
  ReferenceLine,
} from 'recharts'

function ForecastTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  const d = payload[0]?.payload
  
  return (
    <div style={{
      background:   'var(--bg-overlay)',
      border:       '1px solid var(--border-muted)',
      borderRadius: 6,
      padding:      '10px 14px',
      pointerEvents: 'none',
    }}>
      <div style={{
        fontSize:     10,
        color:        'var(--text-ghost)',
        marginBottom: 6,
        textTransform: 'uppercase',
        letterSpacing: '1px',
      }}>
        {label}
      </div>
      <div style={{
        fontSize:   15,
        fontWeight: 700,
        color:      'var(--teal)',
        marginBottom: 4,
      }}>
        ₹{Math.round(d?.projected).toLocaleString('en-IN')}/sqft
      </div>
      <div style={{
        fontSize: 11,
        color:    'var(--text-secondary)',
      }}>
        Range: ₹{Math.round(d?.lower).toLocaleString('en-IN')} — ₹{Math.round(d?.upper).toLocaleString('en-IN')}
      </div>
      <div style={{
        fontSize:   10,
        color:      d?.confidence === 'HIGH'
          ? 'var(--green)'
          : d?.confidence === 'MEDIUM'
            ? 'var(--amber)'
            : 'var(--text-ghost)',
        marginTop:  4,
        fontWeight: 600,
      }}>
        {d?.confidence} confidence
      </div>
    </div>
  )
}

export default function ForecastChart({ forecastData, currentMedian, city }) {
  const chartData = useMemo(() => {
    if (!forecastData?.length) return []
    return forecastData.map(p => ({
      label:      p.horizon_label,
      projected:  p.projected_price,
      lower:      p.lower_bound,
      upper:      p.upper_bound,
      confidence: p.confidence,
    }))
  }, [forecastData])
  
  if (!chartData.length) return null
  
  return (
    <div style={{
      background:   'var(--bg-base)',
      border:       '1px solid var(--border-subtle)',
      borderRadius: 8,
      padding:      20,
    }}>
      <div style={{ marginBottom: 4 }}>
        <span style={{
          fontSize:   13,
          fontWeight: 700,
          color:      'var(--text-primary)',
        }}>
          Price Forecast — {city}
        </span>
      </div>
      <div style={{
        fontSize:     11,
        color:        'var(--text-secondary)',
        marginBottom: 20,
      }}>
        Implied CAGR from 2020→2025 actual data · confidence bands widen with horizon
      </div>
      
      <div style={{ height: 220 }}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart
            data={chartData}
            margin={{ top: 8, right: 16, bottom: 0, left: 8 }}
          >
            <defs>
              <linearGradient id="forecastGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%"  stopColor="#2DD4BF" stopOpacity={0.2} />
                <stop offset="95%" stopColor="#2DD4BF" stopOpacity={0}   />
              </linearGradient>
              <linearGradient id="bandGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%"  stopColor="#2DD4BF" stopOpacity={0.06} />
                <stop offset="95%" stopColor="#2DD4BF" stopOpacity={0}    />
              </linearGradient>
            </defs>
            
            <XAxis
              dataKey="label"
              tick={{ fontSize: 11, fill: 'var(--text-ghost)', fontFamily: 'inherit' }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              tickFormatter={v => `₹${(v/1000).toFixed(0)}K`}
              tick={{ fontSize: 10, fill: 'var(--text-ghost)', fontFamily: 'inherit' }}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip content={<ForecastTooltip />} />
            
            {/* Current median reference line */}
            <ReferenceLine
              y={currentMedian}
              stroke="var(--border-muted)"
              strokeDasharray="3 3"
              strokeWidth={1}
              label={{
                value:    'Current',
                position: 'insideTopLeft',
                fontSize: 9,
                fill:     'var(--text-ghost)',
                fontFamily: 'inherit',
              }}
            />
            
            {/* Confidence band — upper */}
            <Area
              type="monotone"
              dataKey="upper"
              stroke="none"
              fill="url(#bandGrad)"
              isAnimationActive
              animationDuration={1200}
            />
            
            {/* Confidence band — lower */}
            <Area
              type="monotone"
              dataKey="lower"
              stroke="none"
              fill="#FFFFFF"
              isAnimationActive={false}
            />
            
            {/* Main forecast line */}
            <Area
              type="monotone"
              dataKey="projected"
              stroke="var(--teal)"
              strokeWidth={2}
              fill="url(#forecastGrad)"
              dot={{
                r:           5,
                fill:        'var(--teal)',
                strokeWidth: 2,
                stroke:      'var(--bg-base)',
              }}
              activeDot={{
                r:           6,
                fill:        'var(--teal)',
                strokeWidth: 0,
              }}
              isAnimationActive
              animationDuration={1400}
              animationEasing="ease-out"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
