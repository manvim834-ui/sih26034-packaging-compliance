import cv2
import numpy as np


def detect_mrp_tampering(
    image_path,
    mrp_bbox=None
):

    image = cv2.imread(image_path)

    if image is None:
        return {
            "status": "REVIEW",
            "reason": "Unable to read image",
            "legal_reference": "Rule 6(3)"
        }

    # --------------------------------------------------
    # If OCR provides an MRP bounding box, use it
    # --------------------------------------------------

    if mrp_bbox is None:
        return {
            "status": "REVIEW",
            "reason": (
                "MRP location could not be determined "
                "reliably from OCR"
            ),
            "legal_reference": "Rule 6(3)"
        }

    points = np.array(
        mrp_bbox,
        dtype=np.int32
    )

    x, y, w, h = cv2.boundingRect(points)

    # Add a small surrounding region
    padding = 20

    x1 = max(0, x - padding)
    y1 = max(0, y - padding)
    x2 = min(image.shape[1], x + w + padding)
    y2 = min(image.shape[0], y + h + padding)

    roi = image[y1:y2, x1:x2]

    if roi.size == 0:
        return {
            "status": "REVIEW",
            "reason": "Invalid MRP region",
            "legal_reference": "Rule 6(3)"
        }

    # --------------------------------------------------
    # Detect strong rectangular/sticker-like regions
    # --------------------------------------------------

    gray = cv2.cvtColor(
        roi,
        cv2.COLOR_BGR2GRAY
    )

    edges = cv2.Canny(
        gray,
        50,
        150
    )

    contours, _ = cv2.findContours(
        edges,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    sticker_like = False

    roi_area = roi.shape[0] * roi.shape[1]

    for contour in contours:

        area = cv2.contourArea(contour)

        if area <= 0:
            continue

        x_c, y_c, w_c, h_c = cv2.boundingRect(
            contour
        )

        contour_area_ratio = area / roi_area

        if (
            contour_area_ratio > 0.20
            and w_c > 30
            and h_c > 10
        ):
            sticker_like = True
            break

    if sticker_like:

        return {
            "status": "FLAG",
            "reason": (
                "Potential sticker/covering detected "
                "near MRP region"
            ),
            "legal_reference": "Rule 6(3)"
        }

    return {
        "status": "PASS",
        "reason": (
            "No obvious sticker-like covering detected "
            "near MRP region"
        ),
        "legal_reference": "Rule 6(3)"
    }