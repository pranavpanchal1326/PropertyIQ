import { useEffect, useRef } from 'react'
import { motion } from 'framer-motion'

// ── City center coordinates ────────────────────────────────────────────────
const CITY_CENTERS = {
  'Mumbai':      { lat: 19.0760, lng: 72.8777, zoom: 12 },
  'Delhi':       { lat: 28.6139, lng: 77.2090, zoom: 11 },
  'Bengaluru':   { lat: 12.9716, lng: 77.5946, zoom: 12 },
  'Hyderabad':   { lat: 17.3850, lng: 78.4867, zoom: 12 },
  'Pune':        { lat: 18.5204, lng: 73.8567, zoom: 12 },
  'Chennai':     { lat: 13.0827, lng: 80.2707, zoom: 12 },
  'Kolkata':     { lat: 22.5726, lng: 88.3639, zoom: 12 },
  'Ahmedabad':   { lat: 23.0225, lng: 72.5714, zoom: 12 },
  'Gurgaon':     { lat: 28.4595, lng: 77.0266, zoom: 12 },
  'Navi Mumbai': { lat: 19.0330, lng: 73.0297, zoom: 12 },
}

// ── Locality coordinate lookup ─────────────────────────────────────────────
// Approximate coords for all 122 localities
const LOCALITY_COORDS = {
  // Mumbai
  'Bandra West':    { lat: 19.0596, lng: 72.8295 },
  'Andheri West':   { lat: 19.1136, lng: 72.8697 },
  'Juhu':           { lat: 19.1075, lng: 72.8263 },
  'Worli':          { lat: 19.0130, lng: 72.8153 },
  'Powai':          { lat: 19.1176, lng: 72.9060 },
  'Malad':          { lat: 19.1887, lng: 72.8486 },
  'Borivali':       { lat: 19.2307, lng: 72.8567 },
  'Chembur':        { lat: 19.0522, lng: 72.8994 },
  'Dadar':          { lat: 19.0178, lng: 72.8478 },
  'Kurla':          { lat: 19.0726, lng: 72.8796 },
  'Lower Parel':    { lat: 18.9948, lng: 72.8258 },
  'Mulund':         { lat: 19.1726, lng: 72.9561 },
  'Vikhroli':       { lat: 19.1074, lng: 72.9269 },
  // Delhi
  'Dwarka':         { lat: 28.5921, lng: 77.0460 },
  'Rohini':         { lat: 28.7041, lng: 77.1025 },
  'Saket':          { lat: 28.5244, lng: 77.2066 },
  'Vasant Kunj':    { lat: 28.5200, lng: 77.1577 },
  'Janakpuri':      { lat: 28.6219, lng: 77.0878 },
  'Lajpat Nagar':   { lat: 28.5677, lng: 77.2433 },
  'Mayur Vihar':    { lat: 28.6092, lng: 77.2955 },
  'Pitampura':      { lat: 28.7001, lng: 77.1309 },
  'Preet Vihar':    { lat: 28.6411, lng: 77.2942 },
  'Shahdara':       { lat: 28.6729, lng: 77.2942 },
  'Uttam Nagar':    { lat: 28.6200, lng: 77.0588 },
  'Connaught Place':{ lat: 28.6315, lng: 77.2167 },
  'Karol Bagh':     { lat: 28.6520, lng: 77.1908 },
  'South Delhi':    { lat: 28.5355, lng: 77.2456 },
  'Dwarka Expressway':{ lat: 28.6110, lng: 77.0380 },
  // Bengaluru
  'Whitefield':       { lat: 12.9698, lng: 77.7499 },
  'Koramangala':      { lat: 12.9352, lng: 77.6245 },
  'Indiranagar':      { lat: 12.9784, lng: 77.6408 },
  'HSR Layout':       { lat: 12.9116, lng: 77.6474 },
  'Marathahalli':     { lat: 12.9591, lng: 77.6971 },
  'Electronic City':  { lat: 12.8445, lng: 77.6604 },
  'Hebbal':           { lat: 13.0352, lng: 77.5970 },
  'JP Nagar':         { lat: 12.9063, lng: 77.5857 },
  'Jayanagar':        { lat: 12.9308, lng: 77.5838 },
  'Rajajinagar':      { lat: 12.9897, lng: 77.5538 },
  'Yelahanka':        { lat: 13.1005, lng: 77.5963 },
  'Devanahalli':      { lat: 13.2471, lng: 77.7111 },
  'Bannerghatta Road':{ lat: 12.8731, lng: 77.5964 },
  'Kengeri':          { lat: 12.9143, lng: 77.4832 },
  'Sarjapur Road':    { lat: 12.9102, lng: 77.6870 },
  'Vijayanagar':      { lat: 12.9719, lng: 77.5368 },
  // Hyderabad
  'HITEC City':       { lat: 17.4435, lng: 78.3772 },
  'Gachibowli':       { lat: 17.4401, lng: 78.3489 },
  'Banjara Hills':    { lat: 17.4156, lng: 78.4347 },
  'Jubilee Hills':    { lat: 17.4318, lng: 78.4071 },
  'Madhapur':         { lat: 17.4484, lng: 78.3915 },
  'Kondapur':         { lat: 17.4600, lng: 78.3615 },
  'Kukatpally':       { lat: 17.4849, lng: 78.3985 },
  'Secunderabad':     { lat: 17.4399, lng: 78.4983 },
  'Ameerpet':         { lat: 17.4374, lng: 78.4487 },
  'Manikonda':        { lat: 17.4062, lng: 78.3904 },
  'Kompally':         { lat: 17.5450, lng: 78.4862 },
  'LB Nagar':         { lat: 17.3473, lng: 78.5523 },
  'Miyapur':          { lat: 17.4962, lng: 78.3596 },
  'Uppal':            { lat: 17.4057, lng: 78.5591 },
  // Pune
  'Kharadi':          { lat: 18.5507, lng: 73.9417 },
  'Hinjewadi':        { lat: 18.5912, lng: 73.7389 },
  'Wakad':            { lat: 18.5985, lng: 73.7632 },
  'Baner':            { lat: 18.5590, lng: 73.7868 },
  'Hadapsar':         { lat: 18.5018, lng: 73.9257 },
  'Koregaon Park':    { lat: 18.5362, lng: 73.8938 },
  'Kalyani Nagar':    { lat: 18.5488, lng: 73.9008 },
  'Viman Nagar':      { lat: 18.5679, lng: 73.9143 },
  'Pimple Saudagar':  { lat: 18.6100, lng: 73.8020 },
  'Pimpri Chinchwad': { lat: 18.6298, lng: 73.7997 },
  'Ambegaon':         { lat: 18.4547, lng: 73.8474 },
  'Undri':            { lat: 18.4645, lng: 73.9012 },
  // Chennai
  'Adyar':            { lat: 13.0012, lng: 80.2565 },
  'Anna Nagar':       { lat: 13.0878, lng: 80.2105 },
  'T Nagar':          { lat: 13.0418, lng: 80.2341 },
  'Nungambakkam':     { lat: 13.0569, lng: 80.2425 },
  'Velachery':        { lat: 12.9815, lng: 80.2209 },
  'Sholinganallur':   { lat: 12.9010, lng: 80.2279 },
  'Tambaram':         { lat: 12.9249, lng: 80.1000 },
  'Perambur':         { lat: 13.1166, lng: 80.2342 },
  'Chromepet':        { lat: 12.9516, lng: 80.1462 },
  'Porur':            { lat: 13.0359, lng: 80.1566 },
  'Ambattur':         { lat: 13.1143, lng: 80.1548 },
  'Perungudi':        { lat: 12.9566, lng: 80.2453 },
  // Kolkata
  'Salt Lake':        { lat: 22.5830, lng: 88.4180 },
  'New Town':         { lat: 22.6260, lng: 88.4626 },
  'Park Street':      { lat: 22.5510, lng: 88.3510 },
  'Ballygunge':       { lat: 22.5182, lng: 88.3629 },
  'Howrah':           { lat: 22.5958, lng: 88.2636 },
  'Tollygunge':       { lat: 22.4948, lng: 88.3469 },
  'Behala':           { lat: 22.4981, lng: 88.3173 },
  'Rajarhat':         { lat: 22.6287, lng: 88.4756 },
  'Dum Dum':          { lat: 22.6387, lng: 88.3854 },
  'Garia':            { lat: 22.4726, lng: 88.3847 },
  // Ahmedabad
  'Prahlad Nagar':    { lat: 23.0225, lng: 72.5062 },
  'SG Highway':       { lat: 23.0280, lng: 72.5050 },
  'Satellite':        { lat: 23.0218, lng: 72.5101 },
  'Bopal':            { lat: 23.0423, lng: 72.4710 },
  'Gota':             { lat: 23.1019, lng: 72.5265 },
  'Chandkheda':       { lat: 23.1072, lng: 72.5890 },
  'Maninagar':        { lat: 22.9932, lng: 72.6008 },
  'Naranpura':        { lat: 23.0653, lng: 72.5649 },
  'Vastral':          { lat: 23.0197, lng: 72.6578 },
  'Naroda':           { lat: 23.0925, lng: 72.6440 },
  // Gurgaon
  'DLF Phase 1':      { lat: 28.4760, lng: 77.0938 },
  'Golf Course Road': { lat: 28.4679, lng: 77.0999 },
  'Sohna Road':       { lat: 28.4156, lng: 77.0398 },
  'Sector 56':        { lat: 28.4178, lng: 77.1025 },
  'Sector 82':        { lat: 28.4350, lng: 76.9780 },
  'Palam Vihar':      { lat: 28.5034, lng: 76.9929 },
  'New Palam Vihar':  { lat: 28.4862, lng: 76.9780 },
  'Manesar':          { lat: 28.3580, lng: 76.9320 },
  'Vatika City':      { lat: 28.4076, lng: 77.0503 },
  // Navi Mumbai
  'Kharghar':         { lat: 19.0474, lng: 73.0659 },
  'Vashi':            { lat: 19.0771, lng: 73.0071 },
  'Nerul':            { lat: 19.0377, lng: 73.0152 },
  'Belapur':          { lat: 19.0190, lng: 73.0390 },
  'Panvel':           { lat: 18.9894, lng: 73.1175 },
  'Airoli':           { lat: 19.1554, lng: 72.9990 },
  'Ghansoli':         { lat: 19.1272, lng: 73.0125 },
  'Sanpada':          { lat: 19.0597, lng: 73.0139 },
}

// ── Map component ──────────────────────────────────────────────────────────
export default function PropertyMap({ city, locality }) {
  const mapRef       = useRef(null)
  const mapInstance  = useRef(null)
  const markerRef    = useRef(null)
  const containerId  = 'property-map-container'
  
  const cityCenter = CITY_CENTERS[city] || CITY_CENTERS['Mumbai']
  const localCoords = locality ? LOCALITY_COORDS[locality] : null
  
  useEffect(() => {
    // Dynamically import Leaflet to avoid SSR issues
    async function initMap() {
      const L = (await import('leaflet')).default
      await import('leaflet/dist/leaflet.css')
      
      // Fix default marker icon issue with webpack/vite
      delete L.Icon.Default.prototype._getIconUrl
      L.Icon.Default.mergeOptions({
        iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
        iconUrl:       'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
        shadowUrl:     'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
      })
      
      const container = document.getElementById(containerId)
      if (!container) return
      
      // Init map only once
      if (!mapInstance.current) {
        mapInstance.current = L.map(containerId, {
          zoomControl:       true,
          scrollWheelZoom:   false,
          attributionControl: false,
        }).setView([cityCenter.lat, cityCenter.lng], cityCenter.zoom)
        
        // Clean minimal tile layer — CartoDB light
        L.tileLayer(
          'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
          { maxZoom: 18 }
        ).addTo(mapInstance.current)
      }
    }
    
    initMap()
    
    return () => {
      if (mapInstance.current) {
        mapInstance.current.remove()
        mapInstance.current = null
      }
    }
  }, [])
  
  // Pan to city when city changes
  useEffect(() => {
    if (!mapInstance.current) return
    mapInstance.current.flyTo(
      [cityCenter.lat, cityCenter.lng],
      cityCenter.zoom,
      { duration: 0.8 }
    )
  }, [city])
  
  // Drop marker on locality when selected
  useEffect(() => {
    async function updateMarker() {
      if (!mapInstance.current) return
      const L = (await import('leaflet')).default
      
      // Remove old marker
      if (markerRef.current) {
        markerRef.current.remove()
        markerRef.current = null
      }
      
      if (!localCoords) return
      
      // Custom teal marker
      const tealIcon = L.divIcon({
        className: '',
        html: `
          <div style="
            width: 32px; height: 32px;
            background: #0D9488;
            border: 3px solid #FFFFFF;
            border-radius: 50% 50% 50% 0;
            transform: rotate(-45deg);
            box-shadow: 0 2px 8px rgba(13,148,136,0.5);
          "></div>
        `,
        iconSize:   [32, 32],
        iconAnchor: [16, 32],
      })
      
      markerRef.current = L.marker(
        [localCoords.lat, localCoords.lng],
        { icon: tealIcon }
      )
        .addTo(mapInstance.current)
        .bindPopup(`
          <div style="font-family:'Plus Jakarta Sans',sans-serif; padding:4px 2px;">
            <div style="font-weight:700; font-size:13px; color:#1F2328;">${locality}</div>
            <div style="font-size:11px; color:#656D76; margin-top:2px;">${city}</div>
          </div>
        `, { maxWidth: 200 })
        .openPopup()
      
      mapInstance.current.flyTo(
        [localCoords.lat, localCoords.lng],
        14,
        { duration: 0.9 }
      )
    }
    
    updateMarker()
  }, [locality, city])
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0  }}
      transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
      style={{
        borderRadius: 8,
        overflow:     'hidden',
        border:       '1px solid #D0D7DE',
      }}
    >
      {/* Map header */}
      <div style={{
        padding:        '10px 16px',
        background:     '#F6F8FA',
        borderBottom:   '1px solid #D0D7DE',
        display:        'flex',
        alignItems:     'center',
        justifyContent: 'space-between',
      }}>
        <span style={{
          fontSize:   12,
          fontWeight: 600,
          color:      '#1F2328',
        }}>
          {locality ? `${locality}, ${city}` : city}
        </span>
        {localCoords && (
          <span style={{
            fontSize:     10,
            color:        '#0D9488',
            fontWeight:   600,
            background:   '#0D948812',
            border:       '1px solid #0D948830',
            borderRadius: 4,
            padding:      '2px 8px',
          }}>
            Located
          </span>
        )}
        {!localCoords && locality && (
          <span style={{
            fontSize:     10,
            color:        '#9A6700',
            fontWeight:   600,
            background:   '#9A670012',
            border:       '1px solid #9A670030',
            borderRadius: 4,
            padding:      '2px 8px',
          }}>
            City view
          </span>
        )}
      </div>
      
      {/* Map container */}
      <div
        id={containerId}
        style={{ height: 260, width: '100%' }}
      />
    </motion.div>
  )
}
