import { useEffect, useMemo, useState } from "react";
import { fetchHistory } from "../api/client";
import VerdictBadge from "../components/VerdictBadge";

export default function HistoryPage() {
  const [scans, setScans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [search, setSearch] = useState("");
  const [verdict, setVerdict] = useState("all");

  useEffect(() => {
    const loadHistory = async () => {
      try {
        setLoading(true);

        const data = await fetchHistory();

        setScans(data);
      } catch (err) {
        console.error(err);
        setError(
          "Unable to load scan history."
        );
      } finally {
        setLoading(false);
      }
    };

    loadHistory();
  }, []);

  const filteredScans = useMemo(() => {
    return scans.filter((scan) => {
      const productName =
        scan.product_name ||
        scan.product_id ||
        scan.scan_id ||
        "";

      const matchesSearch =
        productName
          .toLowerCase()
          .includes(search.toLowerCase());

      const scanVerdict =
        scan.overall_status
          ?.toUpperCase()
          .replaceAll(" ", "_");

      const matchesVerdict =
        verdict === "all" ||
        scanVerdict === verdict;

      return matchesSearch && matchesVerdict;
    });
  }, [scans, search, verdict]);

  return (
    <div className="history-page">
      <div className="page-title-section">
        <div>
          <h1>Scan History</h1>
          <p>
            View and search previously scanned
            packaged commodities.
          </p>
        </div>
      </div>

      <div className="history-filters">
        <input
          type="search"
          placeholder="Search product or scan ID..."
          value={search}
          onChange={(e) =>
            setSearch(e.target.value)
          }
        />

        <select
          value={verdict}
          onChange={(e) =>
            setVerdict(e.target.value)
          }
        >
          <option value="all">
            All Verdicts
          </option>

          <option value="COMPLIANT">
            Compliant
          </option>

          <option value="NON_COMPLIANT">
            Non-Compliant
          </option>

          <option value="NEEDS_REVIEW">
            Needs Review
          </option>
        </select>
      </div>

      {loading && (
        <div className="page-message">
          Loading scan history...
        </div>
      )}

      {error && (
        <div className="page-error">
          {error}
        </div>
      )}

      {!loading && !error && (
        <div className="history-table-wrapper">
          <table className="history-table">
            <thead>
              <tr>
                <th>Scan ID</th>
                <th>Product</th>
                <th>Category</th>
                <th>Verdict</th>
                <th>Scanned</th>
              </tr>
            </thead>

            <tbody>
              {filteredScans.map((scan) => (
                <tr key={scan.scan_id}>
                  <td>{scan.scan_id}</td>

                  <td>
                    {scan.product_name ||
                      scan.product_id ||
                      "Unknown Product"}
                  </td>

                  <td>
                    {scan.category ||
                      scan.package_type ||
                      "N/A"}
                  </td>

                  <td>
                    <VerdictBadge
                      verdict={
                        scan.overall_status
                      }
                    />
                  </td>

                  <td>
                    {scan.timestamp
                      ? new Date(
                          scan.timestamp
                        ).toLocaleString(
                          "en-IN"
                        )
                      : "N/A"}
                  </td>
                </tr>
              ))}

              {filteredScans.length === 0 && (
                <tr>
                  <td
                    colSpan="5"
                    className="history-empty"
                  >
                    No scan records found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}