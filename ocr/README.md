# OCR module

Part of the Packaging Compliance Scanner (Smart India Hackathon 2026, SIH26034). See the [main README](../README.md) for the whole system.

I built this module.


## What it does

The module turns one or more package photos into structured text lines that the rule engine can check.

- **Text recognition:** EasyOCR with its pretrained models, used as-is. We did not fine-tune them, because we did not have enough labelled package images.
- **Preprocessing variants:** each image is run through several preprocessed versions, and the results are combined, so that text missed in one version can be found in another.
- **Image-quality checks:** measures blur, contrast, glare and image size, so poor photos are flagged as unreliable instead of being judged.
- **Multi-image aggregation:** runs the pipeline over several photos of the same product (front, back, side) and keeps the source image for every text line.
- **Confidence filtering:** lines below a confidence threshold (default 0.60) are handled separately.
- **Output:** a list of text lines, each with its text, confidence and bounding box, plus the field it probably belongs to. The rule engine and the MRP tampering check use this output.

### Using it

```python
from ocr.ocr_pipeline import run_ocr_pipeline

result = run_ocr_pipeline("backend/test_image.jpg", keep_all_variants=False)
print(result["status"])
for line in result["lines"]:
    print(line["text"])
```

Dependencies for this module: `easyocr`, `opencv-python`, `numpy`.

## Limitations

- The OCR models are not fine-tuned, so accuracy depends heavily on photo quality and on the printing style of the label.
- We have not measured OCR accuracy on a labelled test set.
