import UploadForm from './components/UploadForm';
import DiffViewer from './components/DiffViewer';
import RemoteCollector from './components/RemoteCollector';
import { useState } from 'react';

function App() {
  const [diffData, setDiffData] = useState(null);

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <h1 className="text-3xl font-bold mb-6 text-center">🚀 EnvEye Dashboard</h1>

      {/* Remote Collector Section */}
      <RemoteCollector />

      {/* Upload and Compare Section */}
      <div className="mt-10">
        <UploadForm setDiffData={setDiffData} />
        {diffData && <DiffViewer diffData={diffData} />}
      </div>
    </div>
  );
}

export default App;
