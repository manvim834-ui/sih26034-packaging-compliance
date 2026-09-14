export default function MiniBarChart({ data, valueKey, labelKey, formatLabel = (v) => v }) {
  const max = Math.max(...data.map((d) => d[valueKey]), 1);
  return (
    <div className="bar-chart">
      {data.map((d) => (
        <div className="bar-chart__row" key={d[labelKey]}>
          <span className="bar-chart__label">{formatLabel(d[labelKey])}</span>
          <div className="bar-chart__track">
            <div className="bar-chart__fill" style={{ width: `${(d[valueKey] / max) * 100}%` }} />
          </div>
          <span className="bar-chart__value">{d[valueKey]}</span>
        </div>
      ))}
    </div>
  );
}
