export default function VerdictBadge({ verdict }) {
  const normalized = verdict
    ?.toUpperCase()
    .replaceAll(" ", "_");

  let className = "neutral";

  if (normalized === "COMPLIANT") {
    className = "compliant";
  } else if (normalized === "NON_COMPLIANT") {
    className = "non-compliant";
  } else if (normalized === "NEEDS_REVIEW") {
    className = "review";
  }

  return (
    <span className={`history-verdict ${className}`}>
      {verdict
        ? verdict.replaceAll("_", " ")
        : "Unknown"}
    </span>
  );
}