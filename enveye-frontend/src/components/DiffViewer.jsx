import { useState } from "react";
import axios from "axios";

function DiffViewer({ diffData }) {
  const [explanation, setExplanation] = useState("");
  const [loading, setLoading] = useState(false);

  if (!diffData || Object.keys(diffData).length === 0) {
    return <div className="mt-8 text-center text-gray-500">No differences found!</div>;
  }

  const prettifyPath = (path) => {
    return path
      .replace("root", "")
      .replace(/\['/g, " > ")
      .replace(/'\]/g, "")
      .replace(/^ > /, "")
      .trim();
  };

  const handleExplain = async () => {
    try {
      setLoading(true);
      setExplanation("");
      const response = await axios.post("http://127.0.0.1:8000/explain", diffData);
      setExplanation(response.data.explanation);
    } catch (error) {
      console.error("Error explaining differences:", error);
      alert("Failed to get AI explanation.");
    } finally {
      setLoading(false);
    }
  };

  const renderChangeRow = (type, path, oldValue, newValue) => {
    let bgColor = "bg-green-100";

    if (type === "Removed" || type === "Critical") {
      bgColor = "bg-red-100";
    } else if (type === "Changed") {
      bgColor = "bg-yellow-100";
    }

    return (
      <tr key={path} className="border-b">
        <td className={`px-4 py-2 font-semibold text-sm w-32 whitespace-nowrap ${bgColor}`}>{type}</td>
        <td className={`px-4 py-2 text-sm max-w-xs truncate whitespace-nowrap ${bgColor}`}>{prettifyPath(path)}</td>
        <td className={`px-4 py-2 text-sm w-40 whitespace-nowrap ${bgColor}`}>{oldValue ?? "-"}</td>
        <td className={`px-4 py-2 text-sm w-40 whitespace-nowrap ${bgColor}`}>{newValue ?? "-"}</td>
      </tr>
    );
  };

  const parsedRows = [];

  if (diffData.values_changed) {
    for (const path in diffData.values_changed) {
      const change = diffData.values_changed[path];
      parsedRows.push(renderChangeRow("Changed", path, change.old_value, change.new_value));
    }
  }

  if (diffData.dictionary_item_added) {
    for (const path in diffData.dictionary_item_added) {
      parsedRows.push(renderChangeRow("Added", path, "-", diffData.dictionary_item_added[path]));
    }
  }

  if (diffData.dictionary_item_removed) {
    for (const path in diffData.dictionary_item_removed) {
      parsedRows.push(renderChangeRow("Removed", path, diffData.dictionary_item_removed[path], "-"));
    }
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
			<tbody>
			  {parsedRows}
			</tbody>
		  </table>
		</div>
        </div>

        {/* Right Panel - Explain Section */}
        <div className="flex-1 bg-white rounded-lg shadow-lg p-4 flex flex-col">
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
            <div className="bg-purple-100 text-gray-800 p-4 rounded-lg shadow-md overflow-y-auto">
              <h3 className="text-xl font-semibold mb-2">📝 AI Explanation:</h3>
              <p className="whitespace-pre-line">{explanation}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default DiffViewer;
