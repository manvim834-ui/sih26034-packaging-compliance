import { useState } from "react";
import PageHeader from "../components/PageHeader";
import { mockRuleset } from "../mock/scans";
import "../components/PageHeader.css";
import "./History.css";
import "./Admin.css";

export default function Admin() {
  const [rules, setRules] = useState(mockRuleset);
  const [showJson, setShowJson] = useState(false);

  const toggleRule = (id) => {
    setRules((prev) => prev.map((r) => (r.id === id ? { ...r, enabled: !r.enabled } : r)));
  };

  return (
    <div>
      <PageHeader
        title="Ruleset"
        description="The compliance rules the scan engine runs against — data, not code. Toggle a rule off and it stops being enforced immediately."
        action={
          <div className="admin-actions">
            <button className="btn btn--ghost" type="button" onClick={() => setShowJson((v) => !v)}>
              {showJson ? "Hide raw JSON" : "View raw JSON"}
            </button>
            <button className="btn" type="button">
              Add rule
            </button>
          </div>
        }
      />

      <div className={showJson ? "admin-split" : undefined}>
        <table className="data-table">
          <thead>
            <tr>
              <th>Field</th>
              <th>Applies when</th>
              <th>Validator</th>
              <th>Legal ref.</th>
              <th>Enabled</th>
            </tr>
          </thead>
          <tbody>
            {rules.map((rule) => (
              <tr key={rule.id}>
                <td>{rule.field.replace(/_/g, " ")}</td>
                <td className="data-table__muted">{rule.applies_when.join(", ").replace(/_/g, " ")}</td>
                <td className="data-table__muted">{rule.validator}</td>
                <td className="data-table__muted">{rule.legal_reference}</td>
                <td>
                  <input type="checkbox" checked={rule.enabled} onChange={() => toggleRule(rule.id)} aria-label={`Enable ${rule.field} rule`} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {showJson && (
          <pre className="admin-json">
            <code>{JSON.stringify(rules, null, 2)}</code>
          </pre>
        )}
      </div>
    </div>
  );
}
