import UploadForm from './components/UploadForm';
import DiffViewer from './components/DiffViewer';
import { useState } from 'react';

function App() {
  const [diffData, setDiffData] = useState(null);

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <h1 className="text-3xl font-bold mb-6 text-center">🚀 EnvEye Dashboard</h1>
      <UploadForm setDiffData={setDiffData} />
      {diffData && <DiffViewer diffData={diffData} />}
    </div>
  );
}

export default App;
