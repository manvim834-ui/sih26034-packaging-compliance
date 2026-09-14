export default function MiniLineChart({
  data,
  valueKey,
  labelKey,
  height = 170,
}) {
  if (!data || data.length < 2) {
    return (
      <p className="analytics-empty">
        Not enough scan data yet.
      </p>
    );
  }

  const width = 480;
  const padding = 30;

  const max = Math.max(
    ...data.map((d) => d[valueKey]),
    100
  );

  const stepX =
    (width - padding * 2) /
    (data.length - 1);

  const points = data.map((item, index) => {
    const x = padding + index * stepX;

    const y =
      height -
      padding -
      (item[valueKey] / max) *
        (height - padding * 1.7);

    return [x, y];
  });

  const path = points
    .map(
      ([x, y], index) =>
        `${index === 0 ? "M" : "L"}${x},${y}`
    )
    .join(" ");

  return (
    <svg
      viewBox={`0 0 ${width} ${height}`}
      width="100%"
    >
      <path
        d={path}
        fill="none"
        stroke="#2563eb"
        strokeWidth="3"
      />

      {points.map(([x, y], index) => (
        <circle
          key={index}
          cx={x}
          cy={y}
          r="4"
          fill="#2563eb"
        />
      ))}

      {data.map((item, index) => (
        <text
          key={index}
          x={points[index][0]}
          y={height - 8}
          textAnchor="middle"
          fontSize="10"
          fill="#64748b"
        >
          {item[labelKey]}
        </text>
      ))}
    </svg>
  );
}