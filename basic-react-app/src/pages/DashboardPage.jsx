import { useCallback, useEffect, useMemo, useState } from "react";
import "./Dashboard.css";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const normalizeScans = (data) => {
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.results)) return data.results;
  if (Array.isArray(data?.scans)) return data.scans;
  return [];
};

const normalizeStatus = (status) => {
  if (!status) return "UNKNOWN";
  return String(status).trim().toUpperCase().replaceAll(" ", "_");
};

const statusLabel = (status) =>
  normalizeStatus(status).replaceAll("_", " ");

const displayName = (scan) =>
  scan.product_name && scan.product_name !== "unknown"
    ? scan.product_name
    : scan.product_id && scan.product_id !== "unknown"
      ? scan.product_id
      : scan.scan_id || "Unnamed product";

const formatDate = (timestamp) => {
  if (!timestamp) return "Recently";
  const date = new Date(timestamp);
  if (Number.isNaN(date.getTime())) return "Recently";
  return date.toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
};

function MetricIcon({ type }) {
  if (type === "scans") {
    return <span className="dashboard-metric-icon">▣</span>;
  }
  if (type === "compliant") {
    return <span className="dashboard-metric-icon">✓</span>;
  }
  if (type === "noncompliant") {
    return <span className="dashboard-metric-icon">!</span>;
  }
  return <span className="dashboard-metric-icon">%</span>;
}

export default function DashboardPage() {
  const [scans, setScans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [lastUpdated, setLastUpdated] = useState(null);

  const loadDashboard = useCallback(async () => {
    try {
      setLoading(true);
      setError("");

      const response = await fetch(`${API_BASE}/history`);
      if (!response.ok) {
        throw new Error(`Backend returned ${response.status}`);
      }

      const data = await response.json();
      setScans(normalizeScans(data));
      setLastUpdated(new Date());
    } catch (err) {
      console.error("Dashboard data load failed:", err);
      setError(
        "Unable to connect to the compliance backend. Start FastAPI and refresh the dashboard."
      );
      setScans([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDashboard();
  }, [loadDashboard]);

  const insights = useMemo(() => {
    const total = scans.length;
    const compliant = scans.filter(
      (scan) => normalizeStatus(scan.overall_status) === "COMPLIANT"
    ).length;
    const nonCompliant = scans.filter((scan) => {
      const status = normalizeStatus(scan.overall_status);
      return status === "NON_COMPLIANT" || status === "NON-COMPLIANT";
    }).length;
    const review = scans.filter((scan) => {
      const status = normalizeStatus(scan.overall_status);
      return status === "REVIEW" || status === "NEEDS_REVIEW";
    }).length;

    const evaluated = compliant + nonCompliant + review;
    const other = Math.max(total - evaluated, 0);
    const complianceRate = evaluated
      ? Math.round((compliant / evaluated) * 100)
      : 0;

    const violationCounts = {};
    scans.forEach((scan) => {
      if (!scan.violation_type) return;
      String(scan.violation_type)
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean)
        .forEach((item) => {
          violationCounts[item] = (violationCounts[item] || 0) + 1;
        });
    });

    const topViolation = Object.entries(violationCounts).sort(
      (a, b) => b[1] - a[1]
    )[0];

    const categoryCounts = {};
    scans.forEach((scan) => {
      const category =
        scan.category && scan.category !== "unknown"
          ? scan.category
          : scan.package_type && scan.package_type !== "unknown"
            ? scan.package_type
            : null;
      if (category) {
        categoryCounts[category] = (categoryCounts[category] || 0) + 1;
      }
    });

    const topCategory = Object.entries(categoryCounts).sort(
      (a, b) => b[1] - a[1]
    )[0];

    const recent = [...scans]
      .sort((a, b) => {
        const aTime = a.timestamp ? new Date(a.timestamp).getTime() : 0;
        const bTime = b.timestamp ? new Date(b.timestamp).getTime() : 0;
        return bTime - aTime;
      })
      .slice(0, 5);

    return {
      total,
      compliant,
      nonCompliant,
      review,
      other,
      evaluated,
      complianceRate,
      topViolation: topViolation
        ? { name: topViolation[0], count: topViolation[1] }
        : null,
      topCategory: topCategory
        ? { name: topCategory[0], count: topCategory[1] }
        : null,
      recent,
    };
  }, [scans]);

  return (
    <div className="dashboard-page">
      <section className="dashboard-welcome">
        <div className="dashboard-welcome-copy">
          <span className="dashboard-eyebrow">PACKSURE AI • LIVE COMPLIANCE</span>
          <h1>Welcome to PackSure AI</h1>
          <p>
            Monitor packaged-commodity compliance, understand your latest scan
            activity, and identify recurring declaration issues from one place.
          </p>
          <div className="dashboard-live-status">
            <span className="dashboard-live-dot" />
            {loading
              ? "Fetching live scan data..."
              : error
                ? "Backend connection unavailable"
                : `${insights.total} scan${insights.total === 1 ? "" : "s"}`}
          </div>
        </div>

        <div className="dashboard-welcome-art" aria-hidden="true">
          <div className="dashboard-shield">✓</div>
          <div className="dashboard-scan-frame frame-one" />
          <div className="dashboard-scan-frame frame-two" />
        </div>
      </section>

      {error && (
        <div className="dashboard-error">
          <div>
            <strong>Live data unavailable</strong>
            <p>{error}</p>
          </div>
          <button onClick={loadDashboard}>Retry</button>
        </div>
      )}

      <div className="dashboard-section-heading">
        <div>
          <h2>Compliance at a glance</h2>
          <p>Insights calculated from the scans stored by your FastAPI backend.</p>
        </div>
        <button
          className="dashboard-refresh"
          onClick={loadDashboard}
          disabled={loading}
        >
          {loading ? "Refreshing..." : "↻ Refresh"}
        </button>
      </div>

      <section className="dashboard-metrics-grid">
        <article className="dashboard-metric-card metric-total">
          <MetricIcon type="scans" />
          <div>
            <span>Total Scans</span>
            <strong>{insights.total}</strong>
            <small>All stored scans</small>
          </div>
        </article>

        <article className="dashboard-metric-card metric-good">
          <MetricIcon type="compliant" />
          <div>
            <span>Compliant</span>
            <strong>{insights.compliant}</strong>
            <small>{insights.total ? `${Math.round((insights.compliant / insights.total) * 100)}% of all scans` : "No scans yet"}</small>
          </div>
        </article>

        <article className="dashboard-metric-card metric-bad">
          <MetricIcon type="noncompliant" />
          <div>
            <span>Non-Compliant</span>
            <strong>{insights.nonCompliant}</strong>
            <small>Scans with failed checks</small>
          </div>
        </article>

        <article className="dashboard-metric-card metric-rate">
          <MetricIcon type="rate" />
          <div>
            <span>Compliance Rate</span>
            <strong>{insights.complianceRate}%</strong>
            <small>Among evaluated scans</small>
          </div>
        </article>
      </section>

      <section className="dashboard-main-grid">
        <article className="dashboard-panel dashboard-overview-panel">
          <div className="dashboard-panel-heading">
            <div>
              <h3>Compliance Overview</h3>
              <p>Current distribution of scan verdicts</p>
            </div>
          </div>

          <div className="dashboard-overview-content">
            <div
              className="dashboard-donut"
              style={{
                background: `conic-gradient(#247a45 0 ${insights.total ? (insights.compliant / insights.total) * 100 : 0}%, #bd3039 ${insights.total ? (insights.compliant / insights.total) * 100 : 0}% ${insights.total ? ((insights.compliant + insights.nonCompliant) / insights.total) * 100 : 0}%, #a96208 ${insights.total ? ((insights.compliant + insights.nonCompliant) / insights.total) * 100 : 0}% ${insights.total ? ((insights.compliant + insights.nonCompliant + insights.review) / insights.total) * 100 : 0}%, #d8c9c6 ${insights.total ? ((insights.compliant + insights.nonCompliant + insights.review) / insights.total) * 100 : 0}% 100%)`,
              }}
            >
              <div>
                <strong>{insights.total}</strong>
                <span>Total</span>
              </div>
            </div>

            <div className="dashboard-legend">
              <div><span className="legend-dot good" /><span>Compliant</span><strong>{insights.compliant}</strong></div>
              <div><span className="legend-dot bad" /><span>Non-Compliant</span><strong>{insights.nonCompliant}</strong></div>
              <div><span className="legend-dot review" /><span>Needs Review</span><strong>{insights.review}</strong></div>
              {insights.other > 0 && (
                <div><span className="legend-dot other" /><span>Other / No Verdict</span><strong>{insights.other}</strong></div>
              )}
            </div>
          </div>
        </article>

        <article className="dashboard-panel dashboard-insights-panel">
          <div className="dashboard-panel-heading">
            <div>
              <h3>Key Insights</h3>
              <p>Automatically derived from your scan history</p>
            </div>
          </div>

          <div className="dashboard-insight-list">
            <div className="dashboard-insight">
              <div className="insight-icon">!</div>
              <div>
                <span>Most common violation</span>
                <strong>
                  {insights.topViolation
                    ? `${insights.topViolation.name.replaceAll("_", " ")}`
                    : "No violation data yet"}
                </strong>
                {insights.topViolation && (
                  <small>{insights.topViolation.count} occurrence{insights.topViolation.count === 1 ? "" : "s"}</small>
                )}
              </div>
            </div>

            <div className="dashboard-insight">
              <div className="insight-icon">▦</div>
              <div>
                <span>Most scanned category</span>
                <strong>
                  {insights.topCategory
                    ? insights.topCategory.name.replaceAll("_", " ")
                    : "Category data unavailable"}
                </strong>
                {insights.topCategory && (
                  <small>{insights.topCategory.count} scan{insights.topCategory.count === 1 ? "" : "s"}</small>
                )}
              </div>
            </div>

            <div className="dashboard-insight">
              <div className="insight-icon">✓</div>
              <div>
                <span>Evaluation coverage</span>
                <strong>{insights.evaluated} evaluated scan{insights.evaluated === 1 ? "" : "s"}</strong>
                <small>{insights.total ? `${Math.round((insights.evaluated / insights.total) * 100)}% of stored scans have a verdict` : "No scans yet"}</small>
              </div>
            </div>
          </div>
        </article>
      </section>

      <section className="dashboard-panel dashboard-recent-panel">
        <div className="dashboard-panel-heading">
          <div>
            <h3>Recent Scans</h3>
            <p>Latest records available from the backend</p>
          </div>
        </div>

        {loading ? (
          <div className="dashboard-empty-state">Loading live scan history...</div>
        ) : insights.recent.length === 0 ? (
          <div className="dashboard-empty-state">No scans have been recorded yet.</div>
        ) : (
          <div className="dashboard-recent-list">
            {insights.recent.map((scan) => {
              const status = normalizeStatus(scan.overall_status);
              const statusClass =
                status === "COMPLIANT"
                  ? "good"
                  : status === "NON_COMPLIANT" || status === "NON-COMPLIANT"
                    ? "bad"
                    : "review";

              return (
                <div className="dashboard-recent-row" key={scan.scan_id}>
                  <div className="recent-product-icon">▣</div>
                  <div className="recent-product-info">
                    <strong>{displayName(scan)}</strong>
                    <span>Scan ID: {scan.scan_id || "N/A"}</span>
                  </div>
                  <span className={`recent-status ${statusClass}`}>
                    {statusLabel(scan.overall_status)}
                  </span>
                  <span className="recent-date">{formatDate(scan.timestamp)}</span>
                </div>
              );
            })}
          </div>
        )}
      </section>

      <div className="dashboard-footer-note">
        {lastUpdated
          ? `Live data • Last updated ${lastUpdated.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" })}`
          : "Live data from FastAPI backend"}
      </div>
    </div>
  );
}
