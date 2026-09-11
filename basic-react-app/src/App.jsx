import { useRef, useState } from "react";
import HistoryPage from "./pages/HistoryPage";
import AnalyticsPage from "./pages/AnalyticsPage";
import "./App.css";

const formatFieldName = (name) => {
  return name
    .replaceAll("_", " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
};

const displayFieldValue = (value) => {
  if (value === null || value === undefined) {
    return "Not detected";
  }

  if (typeof value === "object") {
    return Object.entries(value)
      .map(([key, val]) => {
        const formattedKey = formatFieldName(key);

        if (typeof val === "boolean") {
          return `${formattedKey}: ${val ? "Yes" : "No"}`;
        }

        return `${formattedKey}: ${val ?? "N/A"}`;
      })
      .join(" | ");
  }

  return String(value);
};

function App() {
  const [activePage, setActivePage] = useState("Dashboard");
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const navItems = [
    {
      name: "Dashboard",
      icon: (
        <svg viewBox="0 0 24 24">
          <path d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z" />
        </svg>
      ),
    },
    {
      name: "Scan Product",
      icon: (
        <svg viewBox="0 0 24 24">
          <path d="M4 7V5a1 1 0 011-1h2V2H5a3 3 0 00-3 3v2h2zm14-3a1 1 0 011 1v2h2V5a3 3 0 00-3-3h-2v2h2zM4 17H2v2a3 3 0 003 3h2v-2H5a1 1 0 01-1-1v-2zm16 0v2a1 1 0 01-1 1h-2v2h2a3 3 0 003-3v-2h-2z" />
        </svg>
      ),
    },
    {
      name: "Scan History",
      icon: (
        <svg viewBox="0 0 24 24">
          <path d="M13 3a9 9 0 00-8.95 8H1l3.89 3.89L8.78 11H7.05A6 6 0 1113 17a5.96 5.96 0 01-4.24-1.76l-1.42 1.42A7.98 7.98 0 1013 3zm-1 5v5l4 2 .75-1.23-3.25-1.92V8H12z" />
        </svg>
      ),
    },
    {
      name: "Analytics",
      icon: (
        <svg viewBox="0 0 24 24">
          <path d="M5 9h3v10H5V9zm5-4h3v14h-3V5zm5 7h3v10h-3V12z" />
        </svg>
      ),
    },
    {
      name: "Settings",
      icon: (
        <svg viewBox="0 0 24 24">
          <path d="M19.43 12.98c.04-.32.07-.65.07-.98s-.02-.66-.07-.98l2.11-1.65-2-3.46-2.49 1a7.12 7.12 0 00-1.69-.98L15 3h-4l-.36 2.53c-.61.25-1.17.58-1.69.98l-2.49-1-2 3.46 2.11 1.65c-.04.32-.08.65-.08.98s.03.66.08.98l-2.11 1.65 2 3.46 2.49-1c.52.4 1.08.73 1.69.98L11 21h4l.36-2.53c.61-.25 1.17-.58 1.69-.98l2.49 1 2-3.46-2.11-1.65zM13 15.5A3.5 3.5 0 1113 8a3.5 3.5 0 010 7.5z" />
        </svg>
      ),
    },
  ];

  return (
    <div className="app">

      {/* ================= SIDEBAR ================= */}

      {/* <aside className="sidebar"> */}
      <aside className={`sidebar ${sidebarOpen ? "open" : "closed"}`}>

        {/* Logo */}
        <div className="sidebar-logo">
          <div className="logo-icon">
            <svg viewBox="0 0 24 24">
              <path d="M12 2L4 5v6c0 5.25 3.4 9.84 8 11 4.6-1.16 8-5.75 8-11V5l-8-3z" />
              <path d="M10.5 14.5L7.5 11.5l1.4-1.4 1.6 1.59 4.6-4.59 1.4 1.41-6 5.99z" />
            </svg>
          </div>

          {/* <div>
            <h1>PackSure AI</h1>
            <p>Legal Metrology Compliance Scanner</p>
          </div> */}
          {sidebarOpen && (
            <div>
              <h1>PackSure AI</h1>
            </div>
          )}
        </div>

        <button
          className="sidebar-toggle"
          onClick={() => setSidebarOpen(!sidebarOpen)}
        >
          {sidebarOpen ? "‹" : "›"}
        </button>

        {/* Navigation */}
        <nav className="sidebar-nav">

          {navItems.map((item) => (
            <button
              key={item.name}
              className={`nav-item ${activePage === item.name ? "active" : ""
                }`}
              onClick={() => setActivePage(item.name)}
            >
              <span className="nav-icon">
                {item.icon}
              </span>

              {/* <span>{item.name}</span> */}
              {sidebarOpen && <span>{item.name}</span>}
            </button>
          ))}

        </nav>



      </aside>


      {/* ================= MAIN AREA ================= */}

      {/* <main className="main-content"> */}
      <main className={`main-content ${sidebarOpen ? "sidebar-open" : "sidebar-closed"}`}>

        {/* Top Navbar */}
        <header className="topbar">



          <div className="topbar-right">



            <div className="profile">

              <div className="profile-avatar">
                <svg viewBox="0 0 24 24">
                  <path d="M12 12a4 4 0 100-8 4 4 0 000 8zm0 2c-4.42 0-8 2.24-8 5v1h16v-1c0-2.76-3.58-5-8-5z" />
                </svg>
              </div>

              <span className="profile-name">
                User
              </span>

            </div>

          </div>

        </header>


        {/* ================= PAGE CONTENT ================= */}

        <div
          style={{
            display: activePage === "Scan Product" ? "block" : "none",
          }}
        >
          <ScanProductPage />
        </div>

        {activePage === "Scan History" && (
          <HistoryPage />
        )}

        {activePage === "Analytics" && (
          <AnalyticsPage />
        )}

        {activePage === "Dashboard" && (
          <BlankPage title="Dashboard" />
        )}

        {activePage === "Scan History" && (
          <BlankPage title="" />
        )}

        {activePage === "Analytics" && (
          <BlankPage title="" />
        )}

        {activePage === "Settings" && (
          <BlankPage title="Settings" />
        )}

      </main>

    </div>
  );
}


/* =========================================================
   SCAN PRODUCT PAGE
   ========================================================= */

function ScanProductPage() {

  const [image, setImage] = useState(null);
  const [imageFile, setImageFile] = useState(null);

  const [scanResult, setScanResult] = useState(null);
  const [scanned, setScanned] = useState(false);
  const [loading, setLoading] = useState(false);

  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  const [cameraOpen, setCameraOpen] = useState(false);
  const [cameraStream, setCameraStream] = useState(null);

  const [scanController, setScanController] = useState(null);

  const [scanMode, setScanMode] = useState("single");

  const [multipleFiles, setMultipleFiles] = useState([]);
  const [multiplePreviews, setMultiplePreviews] = useState([]);

  const [batchResult, setBatchResult] = useState(null);
  const [batchLoading, setBatchLoading] = useState(false);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: "environment",
        },
        audio: false,
      });

      setCameraStream(stream);
      setCameraOpen(true);

      setTimeout(() => {
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      }, 100);

    } catch (error) {
      console.error("Camera error:", error);
      alert("Unable to access camera. Please allow camera permission.");
    }
  };

  const captureImage = async () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;

    if (!video || !canvas) return;

    if (video.videoWidth === 0 || video.videoHeight === 0) {
      alert("Camera is still loading. Please wait.");
      return;
    }

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const context = canvas.getContext("2d");

    context.drawImage(
      video,
      0,
      0,
      video.videoWidth,
      video.videoHeight
    );

    // For displaying preview
    const capturedImage = canvas.toDataURL(
      "image/jpeg",
      0.95
    );

    setImage(capturedImage);

    // Convert captured image → Blob
    const response = await fetch(capturedImage);
    const blob = await response.blob();

    // Convert Blob → File
    const file = new File(
      [blob],
      "camera-capture.jpg",
      {
        type: "image/jpeg"
      }
    );

    // This is what we'll send to FastAPI
    setImageFile(file);

    setScanned(false);
    setScanResult(null);

    stopCamera();
  };

  const stopCamera = () => {
    if (cameraStream) {
      cameraStream.getTracks().forEach((track) => {
        track.stop();
      });
    }

    setCameraStream(null);
    setCameraOpen(false);
  };




  const handleImageUpload = (e) => {
    const file = e.target.files[0];

    if (!file) return;

    // Actual file → will be sent to backend
    setImageFile(file);

    // Preview → displayed in React
    const imageURL = URL.createObjectURL(file);
    setImage(imageURL);

    setScanned(false);
    setScanResult(null);
  };

  const handleMultipleUpload = (e) => {
    const files = Array.from(e.target.files || []);

    if (files.length === 0) return;

    setMultipleFiles(files);

    const previews = files.map((file) =>
      URL.createObjectURL(file)
    );

    setMultiplePreviews(previews);
    setBatchResult(null);
  };

  const removeMultipleImage = (indexToRemove) => {
    setMultipleFiles((prev) =>
      prev.filter((_, index) => index !== indexToRemove)
    );

    setMultiplePreviews((prev) =>
      prev.filter((_, index) => index !== indexToRemove)
    );

    setBatchResult(null);
  };


  const scanProduct = async () => {
    if (!imageFile) {
      alert("Please upload or capture an image first.");
      return;
    }

    // Create a controller for this scan
    const controller = new AbortController();

    setScanController(controller);
    setLoading(true);
    setScanResult(null);
    setScanned(false);

    try {
      const formData = new FormData();

      formData.append("file", imageFile);

      const response = await fetch(
        "http://localhost:8000/scan",
        {
          method: "POST",
          body: formData,

          // Allows Change Image to cancel this request
          signal: controller.signal,
        }
      );

      if (!response.ok) {
        throw new Error(`Backend returned ${response.status}`);
      }

      const result = await response.json();

      console.log("Backend result:", result);

      setScanResult(result);
      setScanned(true);

    } catch (error) {

      // This happens when user clicks Change Image
      if (error.name === "AbortError") {
        console.log("Scan cancelled by user.");
        return;
      }

      console.error("Scan failed:", error);

      alert(
        "Unable to scan the image. Please check that the backend is running."
      );

    } finally {

      setLoading(false);
      setScanController(null);
    }
  };

  const scanMultipleProducts = async () => {
    if (multipleFiles.length === 0) {
      alert("Please select at least one image.");
      return;
    }

    setBatchLoading(true);
    setBatchResult(null);

    try {
      const formData = new FormData();

      const productId = `batch-${Date.now()}`;

      formData.append("product_id", productId);

      multipleFiles.forEach((file) => {
        formData.append("files", file);
      });

      const response = await fetch(
        "http://localhost:8000/batch",
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        throw new Error(`Backend returned ${response.status}`);
      }

      const result = await response.json();

      console.log("Batch backend result:", result);

      setBatchResult(result);
    } catch (error) {
      console.error("Batch scan failed:", error);

      alert(
        "Unable to scan the images. Please check that the backend is running."
      );
    } finally {
      setBatchLoading(false);
    }
  };


  return (

    <div className="page-container">

      {/* HERO */}

      <section className="hero">

        <div className="small-label">
          AI POWERED COMPLIANCE
        </div>

        <h2>
          Scan. Verify. Comply.
        </h2>

        <p>
          Upload a product label to automatically verify
          mandatory packaging declarations.
        </p>

        {/* SCAN MODE TOGGLE */}
        <div className="scan-mode-toggle">

          <button
            className={scanMode === "single" ? "active" : ""}
            onClick={() => {
              setScanMode("single");
              setBatchResult(null);
            }}
          >
            Single Image
          </button>

          <button
            className={scanMode === "multiple" ? "active" : ""}
            onClick={() => {
              setScanMode("multiple");

              setImage(null);
              setImageFile(null);
              setScanned(false);
              setScanResult(null);
            }}
          >
            Multiple Images
          </button>

        </div>

      </section>


      {/* SCANNER GRID */}
      {scanMode === "single" && (
        <div className="scanner-grid">
          {/* ================= LEFT ================= */}
          <section className="panel">

            <div className="panel-header">

              <div>
                <h3>Product Scanner</h3>

                <p>
                  Upload or capture a product label
                </p>
              </div>

            </div>


            {/* IMAGE / UPLOAD */}

            {!image && !cameraOpen && (

              <div className="upload-options">
                {/* UPLOAD IMAGE */}

                <label className="upload-box">

                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleImageUpload}
                    hidden
                  />

                  <div className="upload-icon">
                    ↑
                  </div>

                  <h3>Upload Product Label</h3>

                  <p>PNG, JPG or JPEG</p>

                  <span className="upload-button">
                    Choose Image
                  </span>

                </label>


                {/* CAMERA BUTTON */}

                <button
                  className="camera-button"
                  onClick={startCamera}
                >
                  Open Camera
                </button>

              </div>

            )}

            {cameraOpen && (

              <div className="camera-section">

                <div className="camera-preview">

                  <video
                    ref={videoRef}
                    autoPlay
                    playsInline
                    muted
                  />

                </div>


                <div className="camera-actions">

                  <button
                    className="secondary-button"
                    onClick={stopCamera}
                  >
                    Cancel
                  </button>

                  <button
                    className="capture-button"
                    onClick={captureImage}
                  >
                    Capture Image
                  </button>

                </div>


                <canvas
                  ref={canvasRef}
                  style={{ display: "none" }}
                />

              </div>

            )}


            {/* BUTTONS */}

            {image && !cameraOpen && (
              <>
                <div className="image-wrapper">

                  <img
                    src={image}
                    alt="Captured product"
                    className="product-image"
                  />

                  {/* {scanned && (
                    <>
                      <div className="bounding-box box-one">
                        MRP
                      </div>

                      <div className="bounding-box box-two">
                        NET QTY
                      </div>
                    </>
                  )} */}

                </div>


                {/* BUTTONS AFTER IMAGE */}

                <div className="image-actions">

                  {/* CHANGE IMAGE */}

                  <button
                    className="secondary-button"
                    onClick={() => {

                      // Cancel ongoing backend request
                      if (scanController) {
                        scanController.abort();
                      }

                      // Reset UI
                      setImage(null);
                      setImageFile(null);
                      setScanned(false);
                      setScanResult(null);
                      setLoading(false);

                    }}
                  >
                    Change Image
                  </button>


                  {/* SCAN PRODUCT */}

                  <button
                    className="scan-button"
                    onClick={scanProduct}
                    disabled={loading}
                  >

                    {loading
                      ? "Scanning..."
                      : "Scan Product"
                    }

                  </button>

                </div>

              </>
            )}

          </section>


          {/* ================= RIGHT ================= */}

          <section className="panel results-panel">


            {/* EMPTY */}

            {!scanned && !loading && (

              <div className="empty-results">

                <div className="empty-icon">
                  ✓
                </div>

                <h3>
                  No Scan Results
                </h3>

                <p>
                  Upload a product label and scan it
                  to view compliance results.
                </p>

              </div>

            )}


            {/* LOADING */}

            {loading && (

              <div className="scanning-container">

                <div className="loader"></div>

                <h3>
                  Analysing Product
                </h3>

                <p>
                  Checking mandatory packaging
                  declarations...
                </p>

              </div>

            )}


            {/* RESULTS */}

            {scanResult && (
              <div className="result-container">

                {/* OVERALL RESULT */}
                <div className="result-header">

                  <div>
                    <h2>Compliance Result</h2>

                    <p>
                      Scan ID: <strong>{scanResult.scan_id}</strong>
                    </p>

                    <p>
                      Package Type:{" "}
                      <strong>
                        {scanResult.package_type
                          ? formatFieldName(scanResult.package_type)
                          : "N/A"}
                      </strong>
                    </p>
                  </div>

                  <div
                    className={`overall-status ${scanResult.overall_status === "COMPLIANT"
                      ? "compliant"
                      : "non-compliant"
                      }`}
                  >
                    {scanResult.overall_status?.replaceAll("_", " ")}
                  </div>

                </div>


                {/* VIOLATIONS */}
                {scanResult.violation_type && (
                  <div className="violations-section">

                    <h3>Detected Violations</h3>

                    <div className="violation-list">

                      {scanResult.violation_type
                        .split(",")
                        .map((violation, index) => (
                          <span
                            className="violation-badge"
                            key={index}
                          >
                            {formatFieldName(violation.trim())}
                          </span>
                        ))}

                    </div>

                  </div>
                )}


                {/* DECLARATION CHECKS */}
                <div className="fields-section">

                  <h3>Declaration Checks</h3>

                  <div className="fields-grid">

                    {Object.entries(scanResult.fields || {}).map(
                      ([fieldName, fieldData]) => (

                        <div
                          className="field-card"
                          key={fieldName}
                        >

                          <div className="field-card-header">
                            <h4>
                              {formatFieldName(fieldName)}
                            </h4>

                            <span
                              className={`field-status ${fieldData.status === "PASS"
                                ? "pass"
                                : fieldData.status === "FAIL"
                                  ? "fail"
                                  : "not-applicable"
                                }`}
                            >
                              {fieldData.status?.replaceAll("_", " ")}
                            </span>

                          </div>


                          <div className="field-content">

                            <p>
                              <strong>Detected Value</strong>
                            </p>

                            <p className="detected-value">
                              {displayFieldValue(fieldData.value)}
                            </p>


                            {fieldData.reason && (
                              <>
                                <p>
                                  <strong>Reason</strong>
                                </p>

                                <p>
                                  {fieldData.reason}
                                </p>
                              </>
                            )}


                            {/* {fieldData.legal_reference && (
                              <div className="legal-reference">

                                <strong>
                                  Legal Reference:
                                </strong>{" "}

                                {fieldData.legal_reference}

                              </div>
                            )} */}

                          </div>

                        </div>

                      )
                    )}

                  </div>

                </div>

              </div>
            )}

            {batchResult && (
              <div className="batch-result-container">

                <div className="batch-result-header">

                  <div>

                    <h2>Multi-Image Compliance Result</h2>

                    <p>
                      Batch ID:{" "}
                      <strong>{batchResult.batch_id}</strong>
                    </p>

                    <p>
                      Images Processed:{" "}
                      <strong>{batchResult.images_processed}</strong>
                    </p>

                    <p>
                      Package Type:{" "}
                      <strong>
                        {batchResult.package_type
                          ? formatFieldName(batchResult.package_type)
                          : "N/A"}
                      </strong>
                    </p>

                  </div>


                  <div
                    className={`overall-status ${batchResult.overall_status === "COMPLIANT"
                      ? "compliant"
                      : "non-compliant"
                      }`}
                  >
                    {batchResult.overall_status?.replaceAll("_", " ")}
                  </div>

                </div>


                {batchResult.violation_type && (
                  <div className="violations-section">

                    <h3>Detected Violations</h3>

                    <div className="violation-list">

                      {batchResult.violation_type
                        .split(",")
                        .map((violation, index) => (

                          <span
                            className="violation-badge"
                            key={index}
                          >
                            {formatFieldName(
                              violation.trim()
                            )}
                          </span>

                        ))}

                    </div>

                  </div>
                )}


                <div className="fields-section">

                  <h3>Declaration Checks</h3>

                  <div className="fields-grid">

                    {Object.entries(
                      batchResult.fields || {}
                    ).map(([fieldName, fieldData]) => (

                      <div
                        className="field-card"
                        key={fieldName}
                      >

                        <div className="field-card-header">

                          <h4>
                            {formatFieldName(fieldName)}
                          </h4>

                          <span
                            className={`field-status ${fieldData.status === "PASS"
                              ? "pass"
                              : fieldData.status === "FAIL"
                                ? "fail"
                                : "not-applicable"
                              }`}
                          >
                            {fieldData.status?.replaceAll(
                              "_",
                              " "
                            )}
                          </span>

                        </div>


                        <div className="field-content">

                          <p>
                            <strong>Detected Value</strong>
                          </p>

                          <p className="detected-value">
                            {displayFieldValue(
                              fieldData.value
                            )}
                          </p>

                          {fieldData.reason && (
                            <>
                              <p>
                                <strong>Reason</strong>
                              </p>

                              <p>
                                {fieldData.reason}
                              </p>
                            </>
                          )}

                        </div>

                      </div>

                    ))}

                  </div>

                </div>

              </div>
            )}

          </section>

        </div>
      )}

      {scanMode === "multiple" && (
        <div className="multiple-scan-section">

          <section className="panel">

            <div className="panel-header">

              <div>
                <h3>Multiple Image Scanner</h3>

                <p>
                  Upload different views of the same product
                </p>
              </div>

            </div>


            {/* UPLOAD MULTIPLE IMAGES */}

            {multipleFiles.length === 0 ? (

              <label className="upload-box multiple-upload-box">

                <input
                  type="file"
                  accept="image/*"
                  multiple
                  hidden
                  onChange={handleMultipleUpload}
                />

                <div className="upload-icon">
                  ↑
                </div>

                <h3>
                  Upload Multiple Product Images
                </h3>

                <p>
                  Upload different views of the same product
                </p>

                <p className="upload-hint">
                  Front, back, side or bottom labels
                </p>

                <span className="upload-button">
                  Choose Images
                </span>

              </label>

            ) : (

              <>

                {/* SELECTED IMAGES HEADER */}

                <div className="multiple-upload-header">

                  <div>

                    <h3>
                      Selected Product Images
                    </h3>

                    <p>
                      {multipleFiles.length} image
                      {multipleFiles.length !== 1 ? "s" : ""}
                      {" "}selected
                    </p>

                  </div>


                  <button
                    className="secondary-button"
                    onClick={() => {
                      setMultipleFiles([]);
                      setMultiplePreviews([]);
                      setBatchResult(null);
                    }}
                  >
                    Change Images
                  </button>

                </div>


                {/* IMAGE PREVIEWS */}

                <div className="multiple-preview-grid">

                  {multiplePreviews.map((preview, index) => (

                    <div
                      className="multiple-preview-card"
                      key={preview}
                    >

                      <img
                        src={preview}
                        alt={`Product view ${index + 1}`}
                      />

                      <div className="multiple-preview-info">

                        <span>
                          Image {index + 1}
                        </span>

                        <button
                          onClick={() =>
                            removeMultipleImage(index)
                          }
                        >
                          ×
                        </button>

                      </div>

                    </div>

                  ))}

                </div>


                {/* SCAN BUTTON */}

                <button
                  className="scan-button"
                  disabled={batchLoading}
                  onClick={scanMultipleProducts}
                >
                  {batchLoading
                    ? "Scanning Product..."
                    : `Scan ${multipleFiles.length} Images`}
                </button>

              </>

            )}

          </section>


          {/* MULTI IMAGE RESULT */}

          {batchResult && (
            <section className="panel results-panel batch-result-container">

              <div className="batch-result-header">

                <div>

                  <h2>
                    Multi-Image Compliance Result
                  </h2>

                  <p>
                    Batch ID:{" "}
                    <strong>
                      {batchResult.batch_id}
                    </strong>
                  </p>

                  <p>
                    Images Processed:{" "}
                    <strong>
                      {batchResult.images_processed}
                    </strong>
                  </p>

                  <p>
                    Package Type:{" "}
                    <strong>
                      {batchResult.package_type
                        ? formatFieldName(
                          batchResult.package_type
                        )
                        : "N/A"}
                    </strong>
                  </p>

                </div>


                <div
                  className={`overall-status ${batchResult.overall_status === "COMPLIANT"
                      ? "compliant"
                      : "non-compliant"
                    }`}
                >
                  {batchResult.overall_status?.replaceAll(
                    "_",
                    " "
                  )}
                </div>

              </div>


              {/* VIOLATIONS */}

              {batchResult.violation_type && (
                <div className="violations-section">

                  <h3>
                    Detected Violations
                  </h3>

                  <div className="violation-list">

                    {batchResult.violation_type
                      .split(",")
                      .map((violation, index) => (

                        <span
                          className="violation-badge"
                          key={index}
                        >
                          {formatFieldName(
                            violation.trim()
                          )}
                        </span>

                      ))}

                  </div>

                </div>
              )}


              {/* DECLARATION CHECKS */}

              <div className="fields-section">

                <h3>
                  Declaration Checks
                </h3>

                <div className="fields-grid">

                  {Object.entries(
                    batchResult.fields || {}
                  ).map(
                    ([fieldName, fieldData]) => (

                      <div
                        className="field-card"
                        key={fieldName}
                      >

                        <div className="field-card-header">

                          <h4>
                            {formatFieldName(
                              fieldName
                            )}
                          </h4>

                          <span
                            className={`field-status ${fieldData.status === "PASS"
                                ? "pass"
                                : fieldData.status === "FAIL"
                                  ? "fail"
                                  : "not-applicable"
                              }`}
                          >
                            {fieldData.status?.replaceAll(
                              "_",
                              " "
                            )}
                          </span>

                        </div>


                        <div className="field-content">

                          <p>
                            <strong>
                              Detected Value
                            </strong>
                          </p>

                          <p className="detected-value">
                            {displayFieldValue(
                              fieldData.value
                            )}
                          </p>


                          {fieldData.reason && (
                            <>
                              <p>
                                <strong>
                                  Reason
                                </strong>
                              </p>

                              <p>
                                {fieldData.reason}
                              </p>
                            </>
                          )}

                        </div>

                      </div>

                    )
                  )}

                </div>

              </div>

            </section>
          )}

        </div>
      )}
    </div>

  );
}


/* =========================================================
   BLANK PAGE
   ========================================================= */

function BlankPage({ title }) {

  return (

    <div className="blank-page">

      <h2>{title}</h2>

    </div>

  );

}


export default App;