import { useEffect, useState } from "react";
import PageHeader from "../components/PageHeader";
import MiniLineChart from "../components/MiniLineChart";
import MiniBarChart from "../components/MiniBarChart";
import { fetchHistory } from "../api/client";
import { mockComplianceOverTime, deriveMostViolatedFields, derivePassRateByCategory } from "../mock/scans";
import "../components/PageHeader.css";
import "../components/Charts.css";

export default function Analytics() {
  const [scans, setScans] = useState([]);
  const [dataSource, setDataSource] = useState(null);

  useEffect(() => {
    fetchHistory().then(({ scans, source }) => {
      setScans(scans);
      setDataSource(source);
    });
  }, []);

  if (dataSource === null) {
    return (
      <div>
        <PageHeader title="Analytics" description="Compliance trends across every scan logged so far." />
        <p className="data-table__empty">Loading…</p>
      </div>
    );
  }

  const total = scans.length;
  const compliant = scans.filter((s) => s.overall_status === "compliant").length;
  const nonCompliant = scans.filter((s) => s.overall_status === "non_compliant").length;
  const review = scans.filter((s) => s.overall_status === "needs_review").length;
  const passRateByCategory = derivePassRateByCategory(scans);
  const mostViolatedFields = deriveMostViolatedFields(scans);

  return (
    <div>
      <PageHeader title="Analytics" description="Compliance trends across every scan logged so far." />

      {dataSource === "mock" && (
        <p className="data-source-note-inline">Showing mock data — backend not reachable.</p>
      )}

      <div className="kpi-row">
        <div className="kpi-card">
          <p className="kpi-card__label">Total scans</p>
          <p className="kpi-card__value">{total}</p>
        </div>
        <div className="kpi-card">
          <p className="kpi-card__label">Compliant</p>
          <p className="kpi-card__value kpi-card__value--compliant">
            {total ? Math.round((compliant / total) * 100) : 0}%
          </p>
        </div>
        <div className="kpi-card">
          <p className="kpi-card__label">Non-compliant</p>
          <p className="kpi-card__value kpi-card__value--noncompliant">
            {total ? Math.round((nonCompliant / total) * 100) : 0}%
          </p>
        </div>
        <div className="kpi-card">
          <p className="kpi-card__label">Needs review</p>
          <p className="kpi-card__value kpi-card__value--review">
            {total ? Math.round((review / total) * 100) : 0}%
          </p>
        </div>
      </div>

      <div className="analytics-grid">
        <div className="panel">
          <p className="panel__label">Compliance rate over time</p>
          {/* TODO: /history doesn't return a time-bucketed trend yet — this
              chart still uses placeholder data until that's derivable from
              real timestamps (needs enough historical scans to bucket by day). */}
          <MiniLineChart data={mockComplianceOverTime} valueKey="rate" labelKey="date" />
        </div>
        <div className="panel">
          <p className="panel__label">Pass rate by category</p>
          {passRateByCategory.length > 0 ? (
            <MiniBarChart data={passRateByCategory} valueKey="rate" labelKey="category" />
          ) : (
            <p className="data-table__empty">No scans yet.</p>
          )}
        </div>
      </div>

      <div className="panel">
        <p className="panel__label">Most-violated fields</p>
        {mostViolatedFields.length > 0 ? (
          <MiniBarChart data={mostViolatedFields} valueKey="count" labelKey="field" formatLabel={(v) => v.replace(/_/g, " ")} />
        ) : (
          <p className="data-table__empty">No violations logged yet.</p>
        )}
      </div>
    </div>
  );
}
