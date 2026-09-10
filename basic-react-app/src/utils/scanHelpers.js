export function getMostViolatedFields(scans) {
  const counts = {};

  scans.forEach((scan) => {
    Object.entries(scan.fields || {}).forEach(
      ([fieldName, fieldData]) => {
        if (
          fieldData.status?.toUpperCase() === "FAIL"
        ) {
          counts[fieldName] =
            (counts[fieldName] || 0) + 1;
        }
      }
    );
  });

  return Object.entries(counts)
    .map(([field, count]) => ({
      field,
      count,
    }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 6);
}

export function getPassRateByCategory(scans) {
  const categories = {};

  scans.forEach((scan) => {
    const category =
      scan.category ||
      scan.package_type ||
      "Uncategorized";

    if (!categories[category]) {
      categories[category] = {
        total: 0,
        compliant: 0,
      };
    }

    categories[category].total++;

    if (
      scan.overall_status?.toUpperCase() ===
      "COMPLIANT"
    ) {
      categories[category].compliant++;
    }
  });

  return Object.entries(categories).map(
    ([category, values]) => ({
      category,
      rate: Math.round(
        (values.compliant / values.total) * 100
      ),
    })
  );
}

export function getComplianceTrend(scans) {
  const grouped = {};

  scans.forEach((scan) => {
    if (!scan.timestamp) return;

    const date = new Date(scan.timestamp);

    const key = date.toLocaleDateString(
      "en-IN",
      {
        day: "numeric",
        month: "short",
      }
    );

    if (!grouped[key]) {
      grouped[key] = {
        total: 0,
        compliant: 0,
      };
    }

    grouped[key].total++;

    if (
      scan.overall_status?.toUpperCase() ===
      "COMPLIANT"
    ) {
      grouped[key].compliant++;
    }
  });

  return Object.entries(grouped).map(
    ([date, values]) => ({
      date,
      rate: Math.round(
        (values.compliant / values.total) * 100
      ),
    })
  );
}