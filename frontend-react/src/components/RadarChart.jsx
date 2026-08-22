import React from 'react';

export default function RadarChart({ dimensions = [], size = 320 }) {
  if (!dimensions || dimensions.length === 0) return null;

  const center = size / 2;
  const radius = center - 40;
  const total = dimensions.length;

  // Compute (x, y) coordinates for a given index and score (0 to 100)
  const getPoint = (index, value) => {
    const angle = (Math.PI * 2 / total) * index - Math.PI / 2;
    const r = (value / 100) * radius;
    return {
      x: center + r * Math.cos(angle),
      y: center + r * Math.sin(angle),
    };
  };

  // Generate polygon points string
  const polygonPoints = dimensions
    .map((d, i) => {
      const p = getPoint(i, d.score);
      return `${p.x},${p.y}`;
    })
    .join(' ');

  // Threshold rings (35: Green Auto-Approve, 65: Orange Review, 100: Outer)
  const rings = [35, 65, 100];

  return (
    <div className="radar-container">
      <svg width={size} height={size} style={{ overflow: 'visible' }}>
        {/* Background Grid Rings */}
        {rings.map((ringVal) => {
          const ringPoints = dimensions
            .map((_, i) => {
              const p = getPoint(i, ringVal);
              return `${p.x},${p.y}`;
            })
            .join(' ');
          return (
            <polygon
              key={ringVal}
              points={ringPoints}
              fill="none"
              stroke={ringVal === 35 ? '#86efac' : ringVal === 65 ? '#fdba74' : '#e2e8f0'}
              strokeWidth={ringVal === 100 ? '1.5' : '1'}
              strokeDasharray={ringVal === 100 ? 'none' : '3 3'}
            />
          );
        })}

        {/* Axis Spoke Lines */}
        {dimensions.map((_, i) => {
          const outerP = getPoint(i, 100);
          return (
            <line
              key={i}
              x1={center}
              y1={center}
              x2={outerP.x}
              y2={outerP.y}
              stroke="#e2e8f0"
              strokeWidth="1"
            />
          );
        })}

        {/* Risk Profile Filled Polygon */}
        <polygon
          points={polygonPoints}
          fill="rgba(25, 118, 210, 0.2)"
          stroke="#1976d2"
          strokeWidth="2.5"
        />

        {/* Data Point Markers & Labels */}
        {dimensions.map((d, i) => {
          const p = getPoint(i, d.score);
          const labelP = getPoint(i, 118);
          return (
            <g key={i}>
              <circle
                cx={p.x}
                cy={p.y}
                r="4.5"
                fill="#1976d2"
                stroke="#ffffff"
                strokeWidth="1.5"
              />
              <text
                x={labelP.x}
                y={labelP.y}
                textAnchor="middle"
                dominantBaseline="central"
                fontSize="10"
                fontWeight="700"
                fill="#334155"
                fontFamily="Inter, sans-serif"
              >
                {d.name.replace(' Risk', '')} ({d.score})
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}
