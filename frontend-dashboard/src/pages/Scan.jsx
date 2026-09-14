import PageHeader from "../components/PageHeader";
import "../components/PageHeader.css";
import "./Scan.css";

export default function Scan() {
  return (
    <div>
      <PageHeader title="Scan a product" description="Upload a clear label image and we’ll check it against LMPC requirements." />
      <section className="scan-card">
        <div className="scan-card__icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6"><path d="M12 16V4m0 0L8 8m4-4 4 4"/><path d="M5 14v5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-5"/></svg>
        </div>
        <h2>Upload product label</h2>
        <p>PNG, JPG or WEBP · up to 10 MB</p>
        <button className="btn" type="button">Choose image</button>
      </section>
      <div className="scan-note"><strong>For best results</strong><span>Keep the complete label in frame, use even lighting, and avoid glare.</span></div>
    </div>
  );
}
