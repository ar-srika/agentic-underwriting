import React from 'react';
import { MapPin, Waves, Mountain, Wind, AlertCircle } from 'lucide-react';

export default function LocationIntelligenceCard({ locationIntelligence }) {
  if (!locationIntelligence) return null;

  const {
    geocoding,
    fema_flood,
    usgs_seismic,
    open_meteo_weather,
    composite_location_score,
    mcp_latency_ms,
    hazard_alerts,
  } = locationIntelligence;

  return (
    <div className="enterprise-card">
      <div className="card-header">
        <div className="card-header-left">
          <span>🌍 Real-Time Location Intelligence & MCP Feeds</span>
        </div>
        <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#64748b' }}>
          ⚡ MCP Latency: <b>{mcp_latency_ms || 320}ms</b> · Composite Location Hazard: <b>{composite_location_score}/100</b>
        </span>
      </div>

      <div className="mcp-grid">
        {/* 1. Geocoding */}
        <div className="mcp-subcard mcp-geocoding">
          <div className="mcp-subcard-header">
            <MapPin size={16} />
            <span>📍 Open-Meteo Geocoding</span>
          </div>
          {geocoding ? (
            <div>
              <div className="mcp-stat-row">
                <span className="mcp-stat-key">Coords:</span>
                <span className="mcp-stat-val">{geocoding.latitude?.toFixed(4)}, {geocoding.longitude?.toFixed(4)}</span>
              </div>
              <div className="mcp-stat-row">
                <span className="mcp-stat-key">Elevation:</span>
                <span className="mcp-stat-val">{geocoding.elevation_m}m</span>
              </div>
              <div className="mcp-stat-row">
                <span className="mcp-stat-key">Resolved:</span>
                <span className="mcp-stat-val">{geocoding.city}, {geocoding.state_code || geocoding.state}</span>
              </div>
              <div className="mcp-stat-row">
                <span className="mcp-stat-key">Confidence:</span>
                <span className="mcp-stat-val">{(geocoding.confidence * 100).toFixed(0)}%</span>
              </div>
            </div>
          ) : (
            <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>No geocoding payload</div>
          )}
        </div>

        {/* 2. FEMA Flood Zone */}
        <div className="mcp-subcard mcp-flood">
          <div className="mcp-subcard-header">
            <Waves size={16} />
            <span>🌊 FEMA Flood Zone MCP</span>
          </div>
          {fema_flood ? (
            <div>
              <div className="mcp-stat-row">
                <span className="mcp-stat-key">Zone:</span>
                <span className="mcp-stat-val" style={{ color: fema_flood.is_sfha ? '#dc2626' : '#16a34a' }}>
                  {fema_flood.flood_zone} {fema_flood.is_sfha ? '(🔴 SFHA)' : '(🟢 Minimal)'}
                </span>
              </div>
              <div className="mcp-stat-row">
                <span className="mcp-stat-key">Flood Score:</span>
                <span className="mcp-stat-val">{fema_flood.flood_risk_score}/100</span>
              </div>
              <div className="mcp-stat-row">
                <span className="mcp-stat-key">Annual Prob:</span>
                <span className="mcp-stat-val">{(fema_flood.annual_flood_probability * 100).toFixed(1)}%</span>
              </div>
              <div className="mcp-stat-row">
                <span className="mcp-stat-key">BFE:</span>
                <span className="mcp-stat-val">{fema_flood.base_flood_elevation_ft ? `${fema_flood.base_flood_elevation_ft}ft` : 'N/A'}</span>
              </div>
            </div>
          ) : (
            <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>No flood payload</div>
          )}
        </div>

        {/* 3. USGS Seismic */}
        <div className="mcp-subcard mcp-seismic">
          <div className="mcp-subcard-header">
            <Mountain size={16} />
            <span>🌋 USGS Seismic MCP</span>
          </div>
          {usgs_seismic ? (
            <div>
              <div className="mcp-stat-row">
                <span className="mcp-stat-key">Seismic Zone:</span>
                <span className="mcp-stat-val">{usgs_seismic.seismic_zone}</span>
              </div>
              <div className="mcp-stat-row">
                <span className="mcp-stat-key">Seismic Score:</span>
                <span className="mcp-stat-val">{usgs_seismic.seismic_risk_score}/100</span>
              </div>
              <div className="mcp-stat-row">
                <span className="mcp-stat-key">PGA Intensity:</span>
                <span className="mcp-stat-val">{usgs_seismic.peak_ground_acceleration_g}g</span>
              </div>
              <div className="mcp-stat-row">
                <span className="mcp-stat-key">Fault Proximity:</span>
                <span className="mcp-stat-val">{usgs_seismic.fault_line_proximity_km}km</span>
              </div>
            </div>
          ) : (
            <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>No seismic payload</div>
          )}
        </div>

        {/* 4. Open-Meteo Weather */}
        <div className="mcp-subcard mcp-weather">
          <div className="mcp-subcard-header">
            <Wind size={16} />
            <span>🌪️ Open-Meteo Weather</span>
          </div>
          {open_meteo_weather ? (
            <div>
              <div className="mcp-stat-row">
                <span className="mcp-stat-key">Exposure Tier:</span>
                <span className="mcp-stat-val">{open_meteo_weather.hurricane_exposure_tier}</span>
              </div>
              <div className="mcp-stat-row">
                <span className="mcp-stat-key">Weather Score:</span>
                <span className="mcp-stat-val">{open_meteo_weather.weather_risk_score}/100</span>
              </div>
              <div className="mcp-stat-row">
                <span className="mcp-stat-key">Peak Gusts:</span>
                <span className="mcp-stat-val">{open_meteo_weather.max_wind_gust_mph} mph</span>
              </div>
              <div className="mcp-stat-row">
                <span className="mcp-stat-key">Annual Precip:</span>
                <span className="mcp-stat-val">{open_meteo_weather.annual_precipitation_inches}"</span>
              </div>
            </div>
          ) : (
            <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>No weather payload</div>
          )}
        </div>
      </div>

      {hazard_alerts && hazard_alerts.length > 0 && (
        <div style={{ marginTop: '8px' }}>
          {hazard_alerts.map((alert, i) => (
            <div
              key={i}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '6px 10px',
                background: '#fffbeb',
                border: '1px solid #fde68a',
                borderRadius: '6px',
                fontSize: '0.75rem',
                color: '#92400e',
                marginBottom: '4px'
              }}
            >
              <AlertCircle size={14} color="#d97706" />
              <span>{alert}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
