// Schema confirmed with Person 3 (backend, see Theme_C doc) — a scan looks like:
// {
//   scan_id, batch_id (null unless part of a batch), product_id, product_name,
//   category, overall_status, violation_type (null when compliant), timestamp,
//   fields: { field_name: { value, status } }   <- object keyed by field, not an array
// }
//
// Open questions not yet confirmed (using best-guess values below, flag with
// Person 2/3 if behavior looks off once real data flows in):
// - overall_status: only "compliant" was shown in the example. Assuming
//   "non_compliant" and "needs_review" as the other two values.
// - category vs package_type: the doc's example uses "category" for a
//   product category ("Liquid handwash"), but Theme B's task list also
//   describes a package-type classifier (retail/wholesale/multi_piece/
//   e_commerce). Not clear yet if these are the same field or two separate
//   ones. Filtering below assumes "category" covers both for now.

export const VERDICTS = ["compliant", "non_compliant", "needs_review"];

export const CORE_FIELDS = [
  "manufacturer_name",
  "generic_name",
  "net_quantity",
  "mfg_date",
  "mrp",
  "consumer_care",
  "unit_sale_price",
  "country_of_origin",
];

export const mockScans = [
  {
    scan_id: "001",
    batch_id: null,
    product_id: "p1",
    product_name: "Dettol Sensitive Liquid Handwash",
    category: "Liquid handwash",
    overall_status: "compliant",
    violation_type: null,
    timestamp: "2026-09-03T09:14:00Z",
    fields: {
      manufacturer_name: { value: "Reckitt Benckiser (India) Pvt. Ltd.", status: "pass" },
      net_quantity: { value: "175 ml", status: "pass" },
      mfg_date: { value: "06/26", status: "pass" },
      mrp: { value: "50", status: "pass" },
    },
  },
  {
    scan_id: "002",
    batch_id: null,
    product_id: "p2",
    product_name: "Local Masala Pack 200g",
    category: "Spices",
    overall_status: "non_compliant",
    violation_type: "missing_mandatory_field",
    timestamp: "2026-09-03T10:02:00Z",
    fields: {
      mrp: { value: null, status: "fail" },
      mfg_date: { value: "15/08/2026", status: "pass" },
      country_of_origin: { value: null, status: "fail" },
    },
  },
  {
    scan_id: "003",
    batch_id: "b001",
    product_id: "p3",
    product_name: "Imported Olive Oil 1L",
    category: "Cooking oil",
    overall_status: "needs_review",
    violation_type: "low_ocr_confidence",
    timestamp: "2026-09-02T16:40:00Z",
    fields: {
      unit_sale_price: { value: null, status: "review" },
      mrp: { value: "640", status: "pass" },
    },
  },
  {
    scan_id: "004",
    batch_id: "b001",
    product_id: "p4",
    product_name: "Colgate Toothpaste 100g",
    category: "Personal care",
    overall_status: "compliant",
    violation_type: null,
    timestamp: "2026-09-02T11:20:00Z",
    fields: {
      mrp: { value: "55", status: "pass" },
      consumer_care: { value: "1800-XXX-XXXX", status: "pass" },
    },
  },
];

export const mockComplianceOverTime = [
  { date: "Aug 29", rate: 58 },
  { date: "Aug 30", rate: 62 },
  { date: "Aug 31", rate: 65 },
  { date: "Sep 1", rate: 63 },
  { date: "Sep 2", rate: 68 },
  { date: "Sep 3", rate: 71 },
];

// Proposed ruleset schema — confirm with Person 2 (rules), also flagged as
// unconfirmed in the backend doc ("sanity-check before you lock it").
export const mockRuleset = [
  {
    id: "rule_mrp",
    field: "mrp",
    required: true,
    applies_when: ["retail", "wholesale"],
    validator: "regex",
    legal_reference: "LMPC r.6",
    enabled: true,
  },
  {
    id: "rule_mfg_date",
    field: "mfg_date",
    required: true,
    applies_when: ["retail", "wholesale", "multi_piece", "e_commerce"],
    validator: "date_format",
    legal_reference: "LMPC r.9",
    enabled: true,
  },
  {
    id: "rule_country_of_origin",
    field: "country_of_origin",
    required: true,
    applies_when: ["e_commerce"],
    validator: "presence",
    legal_reference: "LMPC r.11",
    enabled: false,
  },
];

// Derives the "most-violated fields" and "pass rate by category" panels
// from a list of scans, in the real field shape above. Used both for mock
// data and for real data once the API is wired in, so the two paths never
// drift out of sync with each other.
export function deriveMostViolatedFields(scans) {
  const counts = {};
  for (const scan of scans) {
    for (const [fieldName, detail] of Object.entries(scan.fields ?? {})) {
      if (detail.status === "fail") {
        counts[fieldName] = (counts[fieldName] ?? 0) + 1;
      }
    }
  }
  return Object.entries(counts)
    .map(([field, count]) => ({ field, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 6);
}

export function derivePassRateByCategory(scans) {
  const byCategory = {};
  for (const scan of scans) {
    const cat = scan.category ?? "Uncategorized";
    byCategory[cat] ??= { total: 0, compliant: 0 };
    byCategory[cat].total += 1;
    if (scan.overall_status === "compliant") byCategory[cat].compliant += 1;
  }
  return Object.entries(byCategory).map(([category, { total, compliant }]) => ({
    category,
    rate: Math.round((compliant / total) * 100),
  }));
}
