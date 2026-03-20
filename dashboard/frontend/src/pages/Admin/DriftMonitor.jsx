import { motion } from 'framer-motion'
import {
  AlertTriangle,
  BarChart2,
  TrendingUp,
  CheckCircle,
} from 'lucide-react'

import { useDrift }    from '../../hooks/useDrift'
import StatCard        from '../../components/ui/StatCard'
import KSFeatureChart  from '../../components/charts/KSFeatureChart'
import MAPELineChart   from '../../components/charts/MAPELineChart'
import CityDriftTable  from '../../components/tables/CityDriftTable'
import {
  SkeletonStatCard,
  SkeletonChart,
  SkeletonTable,
} from '../../components/ui/SkeletonCard'

// ── Page container animation ───────────────────────────────────────────────
const pageVariants = {
  hidden: {},
  show:   { transition: { staggerChildren: 0.06 } },
}

const sectionVariants = {
  hidden: { opacity: 0, y: 12 },
  show:   {
    opacity: 1,
    y:       0,
    transition: { duration: 0.4, ease: [0.22, 1, 0.36, 1] },
  },
}

// ── Error state ────────────────────────────────────────────────────────────
function ErrorState({ message }) {
  return (
    <div style={{
      display:        'flex',
      flexDirection:  'column',
      alignItems:     'center',
      justifyContent: 'center',
      padding:        '64px 24px',
      gap:            12,
    }}>
      <AlertTriangle size={32} color="var(--red)" strokeWidth={1.5} />
      <div style={{
        fontSize:   14,
        fontWeight: 600,
        color:      'var(--red)',
      }}>
        Failed to load drift data
      </div>
      <div style={{
        fontSize:  12,
        color:     'var(--text-ghost)',
        maxWidth:  400,
        textAlign: 'center',
      }}>
        {message}
      </div>
      <div style={{
        fontSize:    11,
        color:       'var(--text-ghost)',
        fontFamily:  'monospace',
        marginTop:   4,
      }}>
        Make sure the API is running at localhost:8000
      </div>
    </div>
  )
}

// ── Main page ──────────────────────────────────────────────────────────────
export default function DriftMonitor() {
  const { data, loading, error } = useDrift()
  
  if (error) return <ErrorState message={error} />
  
  return (
    <motion.div
      variants={pageVariants}
      initial="hidden"
      animate="show"
      style={{ display: 'flex', flexDirection: 'column', gap: 20 }}
    >
      
      {/* ── KPI Strip ─────────────────────────────────────────── */}
      <motion.div
        variants={sectionVariants}
        style={{
          display:             'grid',
          gridTemplateColumns: 'repeat(4, 1fr)',
          gap:                 16,
        }}
      >
        {loading ? (
          Array(4).fill(0).map((_, i) => <SkeletonStatCard key={i} />)
        ) : (
          <>
            <StatCard
              index={0}
              icon={AlertTriangle}
              label="Drift Severity"
              value={data.summary.overall_severity}
              sub={`${data.summary.drifted_features_count} of ${data.summary.total_features} features crossed threshold`}
              color="red"
              isText
            />
            <StatCard
              index={1}
              icon={BarChart2}
              label="Cities Affected"
              value={`${data.summary.cities_affected} / ${data.summary.total_cities}`}
              sub="All p = 0.0000 · temporal gap 5 years"
              color="amber"
              isText
            />
            <StatCard
              index={2}
              icon={TrendingUp}
              label="Max KS Stat"
              value={data.summary.max_ks_stat}
              sub={`${data.summary.max_ks_city} — threshold 0.30`}
              color="red"
              decimals={4}
            />
            <StatCard
              index={3}
              icon={CheckCircle}
              label="Windows Healthy"
              value={data.mape.pct_healthy}
              sub={`${data.mape.total_windows - data.mape.windows_above_threshold} of ${data.mape.total_windows} below 20% alert`}
              color="green"
              suffix="%"
              decimals={1}
            />
          </>
        )}
      </motion.div>
      
      {/* ── Charts Row ────────────────────────────────────────── */}
      <motion.div
        variants={sectionVariants}
        style={{
          display:             'grid',
          gridTemplateColumns: '1fr 1fr',
          gap:                 16,
        }}
      >
        {loading ? (
          <>
            <SkeletonChart height={240} />
            <SkeletonChart height={240} />
          </>
        ) : (
          <>
            <KSFeatureChart data={data.features} />
            <MAPELineChart  data={data.mape}     />
          </>
        )}
      </motion.div>
      
      {/* ── City Drift Table ──────────────────────────────────── */}
      <motion.div variants={sectionVariants}>
        {loading
          ? <SkeletonTable />
          : <CityDriftTable data={data.cities} />
        }
      </motion.div>
      
      {/* ── Alert recommendation strip ────────────────────────── */}
      {!loading && data?.summary?.recommendation && (
        <motion.div
          variants={sectionVariants}
          style={{
            background:   'var(--red-glow)',
            border:       '1px solid var(--red-border)',
            borderRadius: 8,
            padding:      '14px 20px',
            display:      'flex',
            alignItems:   'flex-start',
            gap:          12,
          }}
        >
          <AlertTriangle
            size={16}
            color="var(--red)"
            strokeWidth={2}
            style={{ flexShrink: 0, marginTop: 1 }}
          />
          <div>
            <div style={{
              fontSize:   11,
              fontWeight: 700,
              color:      'var(--red)',
              marginBottom: 3,
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
            }}>
              System Recommendation
            </div>
            <div style={{
              fontSize:   12,
              color:      'var(--text-secondary)',
              lineHeight: 1.5,
            }}>
              {data.summary.recommendation}
            </div>
          </div>
        </motion.div>
      )}
    </motion.div>
  )
}
