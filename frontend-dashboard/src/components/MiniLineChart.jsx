export default function MiniLineChart({ data, valueKey, labelKey, height = 160 }) {
  const width = 480;
  const padding = 28;
  const max = Math.max(...data.map((d) => d[valueKey]), 100);
  const min = 0;
  const stepX = (width - padding * 2) / (data.length - 1);

  const points = data.map((d, i) => {
    const x = padding + i * stepX;
    const y = height - padding - ((d[valueKey] - min) / (max - min)) * (height - padding * 1.5);
    return [x, y];
  });

  const path = points.map(([x, y], i) => `${i === 0 ? "M" : "L"}${x},${y}`).join(" ");
  const areaPath = `${path} L${points[points.length - 1][0]},${height - padding} L${points[0][0]},${height - padding} Z`;

  return (
    <svg viewBox={`0 0 ${width} ${height}`} width="100%" role="img" aria-label={`Line chart: ${data.map((d) => `${d[labelKey]} ${d[valueKey]}%`).join(", ")}`}>
      <defs>
        <linearGradient id="lineFill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="var(--seal)" stopOpacity="0.35" />
          <stop offset="100%" stopColor="var(--seal)" stopOpacity="0" />
        </linearGradient>
      </defs>
      <path d={areaPath} fill="url(#lineFill)" />
      <path d={path} fill="none" stroke="var(--seal)" strokeWidth="2.5" />
      {points.map(([x, y], i) => (
        <circle key={i} cx={x} cy={y} r="3.5" fill="var(--seal)" stroke="var(--surface-strong)" strokeWidth="1" />
      ))}
      {data.map((d, i) => (
        <text key={i} x={points[i][0]} y={height - 8} fontSize="10" fill="var(--ink-faint)" textAnchor="middle" fontFamily="var(--font-body)">
          {d[labelKey]}
        </text>
      ))}
    </svg>
  );
}
