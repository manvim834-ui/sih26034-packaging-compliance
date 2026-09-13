import { useEffect, useMemo, useState } from "react";
import PageHeader from "../components/PageHeader";
import VerdictBadge from "../components/VerdictBadge";
import { fetchHistory } from "../api/client";
import { VERDICTS } from "../mock/scans";
import "../components/PageHeader.css";
import "./History.css";

export default function History() {
  const [scans, setScans] = useState([]);
  const [dataSource, setDataSource] = useState(null); // "live" | "mock" | null (loading)
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("all");
  const [verdict, setVerdict] = useState("all");

  useEffect(() => {
    fetchHistory().then(({ scans, source }) => {
      setScans(scans);
      setDataSource(source);
    });
  }, []);

  const categories = useMemo(() => [...new Set(scans.map((s) => s.category))], [scans]);

  // TODO: once scan volume grows, move this filtering server-side
  // (GET /history?search=&category=&overall_status=&page=&limit=) instead
  // of filtering the full in-memory list.
  const filtered = useMemo(() => {
    return scans.filter((scan) => {
      const matchesSearch = scan.product_name.toLowerCase().includes(search.toLowerCase());
      const matchesCategory = category === "all" || scan.category === category;
      const matchesVerdict = verdict === "all" || scan.overall_status === verdict;
      return matchesSearch && matchesCategory && matchesVerdict;
    });
  }, [scans, search, category, verdict]);

  return (
    <div>
      <PageHeader
        title="Scan history"
        description="Every scan and batch, searchable and filterable by category, verdict, and date."
        action={
          <button className="btn" type="button">
            Export view
          </button>
        }
      />

      {dataSource === "mock" && (
        <p className="data-source-note">
          Showing mock data — backend not reachable at the configured API URL. Set{" "}
          <code>VITE_API_BASE_URL</code> in <code>.env</code> and make sure the backend is running.
        </p>
      )}

      <div className="filters">
        <input
          type="search"
          placeholder="Search product name…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="filters__search"
        />
        <select value={category} onChange={(e) => setCategory(e.target.value)}>
          <option value="all">All categories</option>
          {categories.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
        <select value={verdict} onChange={(e) => setVerdict(e.target.value)}>
          <option value="all">All verdicts</option>
          {VERDICTS.map((v) => (
            <option key={v} value={v}>
              {v.replace("_", " ")}
            </option>
          ))}
        </select>
      </div>

      <table className="data-table">
        <thead>
          <tr>
            <th>Product</th>
            <th>Category</th>
            <th>Verdict</th>
            <th>Scanned</th>
          </tr>
        </thead>
        <tbody>
          {dataSource === null && (
            <tr>
              <td colSpan={4} className="data-table__empty">
                Loading…
              </td>
            </tr>
          )}
          {dataSource !== null &&
            filtered.map((scan) => (
              <tr key={scan.scan_id}>
                <td>
                  {scan.product_name}
                  {scan.batch_id && <span className="data-table__batch-tag">batch</span>}
                </td>
                <td className="data-table__muted">{scan.category}</td>
                <td>
                  <VerdictBadge verdict={scan.overall_status} />
                </td>
                <td className="data-table__muted">
                  {new Date(scan.timestamp).toLocaleDateString("en-IN", { day: "numeric", month: "short" })}
                </td>
              </tr>
            ))}
          {dataSource !== null && filtered.length === 0 && (
            <tr>
              <td colSpan={4} className="data-table__empty">
                No scans match these filters.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
