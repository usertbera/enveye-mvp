import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'; // 🛠️ Added Router
import UploadForm from './components/UploadForm';
import DiffViewer from './components/DiffViewer';
import RemoteCollector from './components/RemoteCollector';
import SnapshotViewer from './components/SnapshotViewer'; // 🆕 Import SnapshotViewer
import { useEffect } from 'react';

function App() {
  const [diffData, setDiffData] = useState(null);
  
  useEffect(() => {
    document.title = "EnvEye"; // Force set title
  }, []);

  return (
    <Router>
      <div className="min-h-screen bg-gray-100 p-6">
        <h1 className="text-3xl font-bold mb-6 text-center">🚀 EnvEye Dashboard</h1>

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
