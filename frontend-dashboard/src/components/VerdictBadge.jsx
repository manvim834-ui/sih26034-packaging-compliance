const VERDICT_LABELS = {
  compliant: "Compliant",
  non_compliant: "Non-compliant",
  needs_review: "Needs review",
};

/**
 * Shared with the Scan screen (Theme D) so verdicts look identical
 * everywhere in the product. If Person 4 already has one of these,
 * use theirs instead and delete this file.
 */
export default function VerdictBadge({ verdict }) {
  return <span className={`verdict-badge verdict-badge--${verdict}`}>{VERDICT_LABELS[verdict] ?? verdict}</span>;
}
