export default function MiniBarChart({
  data,
  valueKey,
  labelKey,
  formatLabel = (value) => value,
}) {
  const max = Math.max(
    ...data.map((item) => item[valueKey]),
    1
  );

  return (
    <div className="bar-chart">
      {data.map((item) => (
        <div
          className="bar-chart-row"
          key={item[labelKey]}
        >
          <span className="bar-chart-label">
            {formatLabel(item[labelKey])}
          </span>

          <div className="bar-chart-track">
            <div
              className="bar-chart-fill"
              style={{
                width: `${
                  (item[valueKey] / max) * 100
                }%`,
              }}
            />
          </div>

          <span className="bar-chart-value">
            {item[valueKey]}
          </span>
        </div>
      ))}
    </div>
  );
}