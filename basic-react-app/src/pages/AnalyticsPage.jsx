import { useEffect, useState } from "react";

import { fetchHistory } from "../api/client";

import MiniBarChart from "../components/MiniBarChart";
import MiniLineChart from "../components/MiniLineChart";

import {
  getMostViolatedFields,
  getPassRateByCategory,
  getComplianceTrend,
} from "../utils/scanHelpers";

export default function AnalyticsPage() {
  const [scans, setScans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadAnalytics = async () => {
      try {
        const data = await fetchHistory();
        setScans(data);
      } catch (err) {
        console.error(err);

        setError(
          "Unable to load analytics."
        );
      } finally {
        setLoading(false);
      }
    };

    loadAnalytics();
  }, []);

  if (loading) {
    return (
      <div className="page-message">
        Loading analytics...
      </div>
    );
  }

  if (error) {
    return (
      <div className="page-error">
        {error}
      </div>
    );
  }

  const total = scans.length;

  const compliant = scans.filter(
    (scan) =>
      scan.overall_status?.toUpperCase() ===
      "COMPLIANT"
  ).length;

  const nonCompliant = scans.filter(
    (scan) =>
      scan.overall_status?.toUpperCase() ===
      "NON_COMPLIANT"
  ).length;

  const review = scans.filter(
    (scan) =>
      scan.overall_status?.toUpperCase() ===
      "NEEDS_REVIEW"
  ).length;

  const complianceRate =
    total > 0
      ? Math.round(
          (compliant / total) * 100
        )
      : 0;

  const violations =
    getMostViolatedFields(scans);

  const categoryData =
    getPassRateByCategory(scans);

  const trend =
    getComplianceTrend(scans);

  return (
    <div className="analytics-page">
      <div className="page-title-section">
        <div>
          <h1>Analytics</h1>
          <p>
            Monitor compliance trends and common
            Legal Metrology violations.
          </p>
        </div>
      </div>

      <div className="analytics-kpi-grid">
        <div className="analytics-kpi">
          <span>Total Scans</span>
          <strong>{total}</strong>
        </div>

        <div className="analytics-kpi">
          <span>Compliant</span>
          <strong className="analytics-green">
            {compliant}
          </strong>
        </div>

        <div className="analytics-kpi">
          <span>Non-Compliant</span>
          <strong className="analytics-red">
            {nonCompliant}
          </strong>
        </div>

        <div className="analytics-kpi">
          <span>Compliance Rate</span>
          <strong className="analytics-blue">
            {complianceRate}%
          </strong>
        </div>
      </div>

      <div className="analytics-main-grid">
        <div className="analytics-panel">
          <h3>
            Compliance Rate Over Time
          </h3>

          <MiniLineChart
            data={trend}
            valueKey="rate"
            labelKey="date"
          />
        </div>

        <div className="analytics-panel">
          <h3>
            Pass Rate by Category
          </h3>

          {categoryData.length ? (
            <MiniBarChart
              data={categoryData}
              valueKey="rate"
              labelKey="category"
            />
          ) : (
            <p className="analytics-empty">
              No category data available.
            </p>
          )}
        </div>
      </div>

      <div className="analytics-panel">
        <h3>Most Violated Fields</h3>

        {violations.length ? (
          <MiniBarChart
            data={violations}
            valueKey="count"
            labelKey="field"
            formatLabel={(value) =>
              value.replaceAll("_", " ")
            }
          />
        ) : (
          <p className="analytics-empty">
            No violations recorded yet.
          </p>
        )}
      </div>
    </div>
  );
}