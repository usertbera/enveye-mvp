import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import UploadForm from './components/UploadForm';
import DiffViewer from './components/DiffViewer';
import RemoteCollector from './components/RemoteCollector';
import SnapshotViewer from './components/SnapshotViewer';
import logo from './assets/logo_96x96.png'; // ✅ Correct image import

function App() {
  const [diffData, setDiffData] = useState(null);

  useEffect(() => {
    document.title = "EnvEye";
  }, []);

  return (
    <Router>
      <div className="min-h-screen bg-gray-100 p-6">
        {/* ✅ Updated header with actual imported image */}
        <div className="flex justify-center items-center mb-6 space-x-3">
          <img src={logo} alt="EnvEye Logo" className="w-12 h-12 object-contain align-middle mt-[2px]" />
          <h1 className="text-3xl font-bold">EnvEye Dashboard</h1>
        </div>

        {/* Navigation Menu */}
        <div className="flex justify-center space-x-6 mb-8">
          <Link to="/" className="text-blue-600 hover:underline">Home</Link>
          <Link to="/snapshots" className="text-blue-600 hover:underline">Snapshot Viewer</Link>
        </div>

        {/* Routes */}
        <Routes>
          <Route path="/" element={
            <>
              <RemoteCollector />
              <div className="mt-10">
                <UploadForm setDiffData={setDiffData} />
                {diffData && <DiffViewer diffData={diffData} />}
              </div>
            </>
          } />
          <Route path="/snapshots" element={<SnapshotViewer />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
