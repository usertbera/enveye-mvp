import { useState } from 'react';
import axios from 'axios';

function UploadForm({ setDiffData }) {
  const [file1, setFile1] = useState(null);
  const [file2, setFile2] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file1 || !file2) {
      alert("Please upload both files!");
      return;
    }

    const formData = new FormData();
    formData.append('file1', file1);
    formData.append('file2', file2);

    try {
      const response = await axios.post('http://127.0.0.1:8000/compare', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setDiffData(response.data.differences);
    } catch (error) {
      console.error("Error comparing files:", error);
      alert("Failed to compare snapshots. Check backend server!");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow-md space-y-4">
      <div>
        <label className="block mb-1 font-medium">Upload VM-A Snapshot</label>
        <input type="file" onChange={(e) => setFile1(e.target.files[0])} />
      </div>
      <div>
        <label className="block mb-1 font-medium">Upload VM-B Snapshot</label>
        <input type="file" onChange={(e) => setFile2(e.target.files[0])} />
      </div>
      <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
        Compare
      </button>
    </form>
  );
}

export default UploadForm;
