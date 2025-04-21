import { useState } from 'react';
import axios from 'axios';

function RemoteCollector() {
  const [ip, setIp] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [appFolder, setAppFolder] = useState('');
  const [appType, setAppType] = useState('desktop');
  const [status, setStatus] = useState('');
  const [loading, setLoading] = useState(false);

  const handleCollect = async () => {
    if (!ip || !appFolder || !appType) {
      alert("Please fill VM IP, App Folder and App Type!");
      return;
    }

    setLoading(true);
    setStatus('');

    try {
      const response = await axios.post('http://localhost:8000/remote_collect', {
        vm_ip: ip,
        username,
        password,
        app_folder: appFolder,
        app_type: appType
      });

      if (response.data && response.data.status === 'success') {
		  setStatus(`✅ Snapshot collected from ${response.data.vm_hostname}`);
		} else {
		  setStatus("❌ Failed to collect snapshot!");
		}

    } catch (error) {
      console.error(error);
      setStatus("❌ Error during collection!");
    }

    setLoading(false);
  };

  return (
    <div className="p-6 bg-white rounded-lg shadow-md max-w-md mx-auto mt-8">
      <h2 className="text-2xl font-bold mb-4 text-center">🖥️ Remote Snapshot Collector</h2>

      <div className="space-y-4">
        <input
          type="text"
          placeholder="VM IP Address or Hostname"
          value={ip}
          onChange={(e) => setIp(e.target.value)}
          className="w-full px-4 py-2 border rounded focus:outline-none focus:ring"
        />

        <input
          type="text"
          placeholder="Username (optional)"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="w-full px-4 py-2 border rounded focus:outline-none focus:ring"
        />

        <input
          type="password"
          placeholder="Password (optional)"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full px-4 py-2 border rounded focus:outline-none focus:ring"
        />

        <input
          type="text"
          placeholder="Application Folder Path (e.g., C:\\Program Files\\SampleApp)"
          value={appFolder}
          onChange={(e) => setAppFolder(e.target.value)}
          className="w-full px-4 py-2 border rounded focus:outline-none focus:ring"
        />

        <select
          value={appType}
          onChange={(e) => setAppType(e.target.value)}
          className="w-full px-4 py-2 border rounded focus:outline-none focus:ring"
        >
          <option value="desktop">Desktop</option>
          <option value="web">Web</option>
        </select>

        <button
          onClick={handleCollect}
          disabled={loading}
          className="w-full bg-blue-600 text-white font-semibold px-4 py-2 rounded hover:bg-blue-700"
        >
          {loading ? "Collecting..." : "🚀 Collect Snapshot"}
        </button>

        {status && (
          <div className="mt-4 text-center text-sm font-medium">
            {status}
          </div>
        )}
      </div>
    </div>
  );
}

export default RemoteCollector;
