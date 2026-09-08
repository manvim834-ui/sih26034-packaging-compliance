import { useRef, useState } from "react";
import "./App.css";

function App() {
  const [activePage, setActivePage] = useState("Scan Product");
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

        {activePage === "Scan Product" && (
          <ScanProductPage />
        )}

        {activePage === "Dashboard" && (
          <BlankPage title="Dashboard" />
        )}

        {activePage === "Scan History" && (
          <BlankPage title="Scan History" />
        )}

        {activePage === "Analytics" && (
          <BlankPage title="Analytics" />
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
  const [scanned, setScanned] = useState(false);
  const [loading, setLoading] = useState(false);

  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  const [cameraOpen, setCameraOpen] = useState(false);
  const [cameraStream, setCameraStream] = useState(null);

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

  const captureImage = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;

    if (!video || !canvas) return;

    if (video.videoWidth === 0 || video.videoHeight === 0) {
      alert("Camera is still loading. Please wait a moment.");
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

    const capturedImage = canvas.toDataURL(
      "image/jpeg",
      0.95
    );

    setImage(capturedImage);
    setScanned(false);

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

  const result = {
    verdict: "NON_COMPLIANT",

    fields: [
      {
        name: "Maximum Retail Price",
        value: "₹120",
        status: "PASS",
        confidence: 96,
        rule: "MRP declaration detected correctly.",
      },
      {
        name: "Net Quantity",
        value: "500 g",
        status: "PASS",
        confidence: 94,
        rule: "Net quantity and unit are present.",
      },
      {
        name: "Manufacturer Details",
        value: "ABC Foods Pvt. Ltd.",
        status: "PASS",
        confidence: 91,
        rule: "Manufacturer information detected.",
      },
      {
        name: "Manufacturing Date",
        value: "Not detected",
        status: "FAIL",
        confidence: 0,
        rule: "Mandatory manufacturing/packing declaration was not detected.",
      },
      {
        name: "Consumer Care",
        value: "1800-123-456",
        status: "REVIEW",
        confidence: 72,
        rule: "Information detected, but OCR confidence is low.",
      },
    ],
  };


  const handleImageUpload = (event) => {

    const file = event.target.files[0];

    if (!file) return;

    const imageURL = URL.createObjectURL(file);

    setImage(imageURL);
    setScanned(false);
  };


  const scanProduct = () => {

    setLoading(true);

    setTimeout(() => {
      setLoading(false);
      setScanned(true);
    }, 1200);
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

      </section>


      {/* SCANNER GRID */}

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

                {scanned && (
                  <>
                    <div className="bounding-box box-one">
                      MRP
                    </div>

                    <div className="bounding-box box-two">
                      NET QTY
                    </div>
                  </>
                )}

              </div>


              {/* BUTTONS AFTER IMAGE */}

              <div className="image-actions">

                {/* CHANGE IMAGE */}

                <button
                  className="secondary-button"
                  onClick={() => {
                    setImage(null);
                    setScanned(false);
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

          {scanned && (

            <>

              {/* RESULT HEADER */}

              <div className="result-heading">

                <div>

                  <div className="result-label">
                    COMPLIANCE RESULT
                  </div>

                  <h3>
                    Scan Analysis
                  </h3>

                </div>


                <div className="verdict non-compliant">
                  × Non-Compliant
                </div>

              </div>


              {/* SUMMARY */}

              <div className="summary">

                <div>
                  <span>5</span>
                  <p>Fields Checked</p>
                </div>

                <div>
                  <span>3</span>
                  <p>Passed</p>
                </div>

                <div>
                  <span>1</span>
                  <p>Violations</p>
                </div>

              </div>


              {/* FIELD LIST */}

              <div className="field-list">

                {result.fields.map((field, index) => {

                  const statusClass =
                    field.status === "PASS"
                      ? "pass"
                      : field.status === "FAIL"
                        ? "fail"
                        : "review";


                  return (

                    <div
                      className={`field-card ${statusClass}`}
                      key={index}
                    >

                      <div className="field-top">

                        <div>

                          <span className="field-name">
                            {field.name}
                          </span>

                          <h4>
                            {field.value}
                          </h4>

                        </div>


                        <span
                          className={`status-badge ${statusClass}`}
                        >
                          {field.status === "PASS"
                            ? "Passed"
                            : field.status === "FAIL"
                              ? "Failed"
                              : "Needs Review"
                          }
                        </span>

                      </div>


                      {/* CONFIDENCE */}

                      <div className="confidence">

                        <div className="confidence-header">

                          <span>
                            OCR Confidence
                          </span>

                          <span>
                            {field.confidence}%
                          </span>

                        </div>


                        <div className="confidence-bar">

                          <div
                            className={`confidence-fill ${statusClass}`}
                            style={{
                              width: `${field.confidence}%`,
                            }}
                          />

                        </div>

                      </div>


                      {/* RULE */}

                      <div className="rule-text">

                        <strong>
                          Rule Check:
                        </strong>{" "}

                        {field.rule}

                      </div>

                    </div>

                  );

                })}

              </div>

            </>

          )}

        </section>

      </div>

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