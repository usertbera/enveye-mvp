import { useState, useEffect } from "react";
import axios from "axios";
import { API_BASE_URL } from './api';

function DiffViewer({ diffData }) {
  const [explanation, setExplanation] = useState("");
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const [errorScreenshot, setScreenshot] = useState(null);
  const [logPath, setLogPath] = useState("");

  // Scrolls to AI explanation after it gets updated
  useEffect(() => {
    if (explanation) {
      document.getElementById("ai-explanation")?.scrollIntoView({ behavior: "smooth" });
    }
  }, [explanation]);

  // If diffData is missing or empty, show a message
  if (!diffData || Object.keys(diffData).length === 0) {
    return <div className="mt-8 text-center text-gray-500">No differences found!</div>;
  }

  // Helper to prettify the path
  const prettifyPath = (path) => {
    return path
      .replace("root", "")
      .replace(/\['/g, " > ")
      .replace(/'\]/g, "")
      .replace(/^ > /, "")
      .trim();
  };

  // Handling the explanation request to the backend
  const handleExplain = async () => {
    try {
      setLoading(true);
      setExplanation("");

      const payload = {
        diff: diffData,
        error_message: errorMsg || "",
        error_screenshot: errorScreenshot || null,
        log_path: logPath || ""
      };

      const response = await axios.post(`${API_BASE_URL}/explain`, payload);
      setExplanation(response.data.explanation);
    } catch (error) {
      console.error("Error explaining differences:", error);
      alert("Failed to get AI explanation.");
    } finally {
      setLoading(false);
    }
  };

  // Handling the screenshot file upload
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file && file.type.startsWith("image/")) {
      if (file.size > 5 * 1024 * 1024) {
        alert("File too large. Please upload an image smaller than 5MB.");
        return;
      }
      const reader = new FileReader();
      reader.onloadend = () => setScreenshot(reader.result); // Base64 string
      reader.readAsDataURL(file);
    } else {
      alert("Please upload a valid image file.");
    }
  };
  
  //Handle Flags of inaapropriate analysis by AI
  const handleFlagExplanation = async () => {
	  try {
		await axios.post(`${API_BASE_URL}/flag`, {
		  diff: diffData,
		  error_message: errorMsg,
		  explanation: explanation,
		  log_path: logPath
		});
		alert("Thank you! Your feedback has been submitted.");
	  } catch (err) {
		alert("Failed to submit feedback.");
		console.error("Feedback error:", err);
	  }
	};


  // Render the differences as rows
  const renderChangeRow = (type, path, oldValue, newValue, index) => {
	  let bgColor = "bg-green-100";
	  if (type === "Removed" || type === "Critical") bgColor = "bg-red-100";
	  else if (type === "Changed") bgColor = "bg-yellow-100";

	  const renderCell = (value) => {
		if (value === null || value === undefined) return "-";
		if (typeof value === "object") {
		  return (
			<pre className="whitespace-pre-wrap break-words text-xs max-w-xs">
			  {JSON.stringify(value, null, 2)}
			</pre>
		  );
		}
		return value.toString();
	  };

  return (
    <tr key={`${type}-${path}-${index}`} className="border-b">
      <td className={`px-4 py-2 font-semibold text-sm w-32 whitespace-nowrap ${bgColor}`}>{type}</td>
      <td className={`px-4 py-2 text-sm max-w-xs truncate whitespace-nowrap ${bgColor}`}>{prettifyPath(path)}</td>
      <td className={`px-4 py-2 text-sm w-40 whitespace-nowrap ${bgColor}`}>{renderCell(oldValue)}</td>
      <td className={`px-4 py-2 text-sm w-40 whitespace-nowrap ${bgColor}`}>{renderCell(newValue)}</td>
    </tr>
  );
};


  const parsedRows = [];

  // Parsing diff data into rows
  if (diffData.values_changed) {
    Object.entries(diffData.values_changed).forEach(([path, change], index) =>
      parsedRows.push(renderChangeRow("Changed", path, change.old_value, change.new_value, index))
    );
  }
  if (diffData.dictionary_item_added) {
    Object.entries(diffData.dictionary_item_added).forEach(([path, value], index) =>
      parsedRows.push(renderChangeRow("Added", path, "-", value, index))
    );
  }
  if (diffData.dictionary_item_removed) {
    Object.entries(diffData.dictionary_item_removed).forEach(([path, value], index) =>
      parsedRows.push(renderChangeRow("Removed", path, value, "-", index))
    );
  }

  return (
    <div className="min-h-screen p-6 bg-gray-100 text-gray-900">
      <div className="flex justify-center items-center mb-6">
        <h2 className="text-3xl font-bold">🚀 EnvEye - Snapshot Differences</h2>
      </div>

      <div className="flex flex-col md:flex-row gap-6">
        {/* Left Panel - Differences Table */}
        <div className="flex-1 bg-white rounded-lg shadow-lg p-4 overflow-auto max-h-[80vh]">
          <h3 className="text-2xl font-semibold mb-4">🔍 Differences</h3>
          <div className="overflow-x-auto max-h-[70vh] overflow-y-auto border rounded-lg shadow">
            <table className="min-w-full bg-white">
              <thead className="sticky top-0 bg-gray-200">
                <tr className="text-gray-700">
                  <th className="px-4 py-2 text-left">Type</th>
                  <th className="px-4 py-2 text-left">Path</th>
                  <th className="px-4 py-2 text-left">Old Value</th>
                  <th className="px-4 py-2 text-left">New Value</th>
                </tr>
              </thead>
              <tbody>{parsedRows}</tbody>
            </table>
          </div>
        </div>

        {/* Right Panel - Explanation and Inputs */}
        <div className="flex-1 bg-white rounded-lg shadow-lg p-4 flex flex-col">
          <div className="relative mb-4">
            <label htmlFor="error-message" className="sr-only">Error Message</label>
            <textarea
              id="error-message"
              placeholder="Optional: Paste a relevant error message here..."
              className="w-full px-4 py-2 border rounded"
              value={errorMsg}
              onChange={(e) => setErrorMsg(e.target.value)}
            />
            <label
              htmlFor="screenshot-upload"
              className="absolute top-2 right-2 bg-purple-600 text-white px-2 py-1 rounded cursor-pointer text-lg"
              title="Upload Screenshot"
            >
              +
            </label>
            <input
              id="screenshot-upload"
              type="file"
              accept="image/*"
              className="hidden"
              onChange={handleFileChange}
            />
            {errorScreenshot && (
              <p className="text-xs text-gray-500 mt-1">✅ Screenshot uploaded</p>
            )}
          </div>

          {errorScreenshot && (
            <div className="mb-4">
              <img src={errorScreenshot} alt="Screenshot preview" className="max-h-48 rounded shadow" />
            </div>
          )}

          <input
            type="text"
            placeholder="Optional: Enter log file path (e.g., \var\log\myapp\error.log)"
            className="w-full px-4 py-2 border rounded mb-4 text-sm"
            value={logPath}
            onChange={(e) => setLogPath(e.target.value)}
          />

          <div className="flex justify-center mb-4">
            <button
              onClick={handleExplain}
              disabled={loading}
              className="bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-6 rounded transition duration-200"
            >
              {loading ? "🧠 Thinking..." : "🧠 Explain Differences"}
            </button>
          </div>

          {explanation && (
            <div id="ai-explanation" className="bg-purple-100 text-gray-800 p-4 rounded-lg shadow-md overflow-y-auto">
              <h3 className="text-xl font-semibold mb-2">📝 AI Explanation:</h3>
              <p className="whitespace-pre-line">{explanation}</p>
			  
			   <button
				  onClick={handleFlagExplanation}
				  className="mt-4 text-sm text-red-600 underline hover:text-red-800"
				>
				  ⚠️ Flag this explanation as inaccurate
				</button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default DiffViewer;
