import { useState, useCallback, useEffect } from "react";

interface UploadedFile {
  id: string;
  name: string;
  size: number;
}

interface FileResponse {
  name: string;
  size: number;
}

function FileUpload() {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<{ [key: string]: string }>(
    {}
  );
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    // Fetch initial files from the specified folder
    const fetchInitialFiles = async () => {
      try {
        const response = await fetch("http://localhost:8000/api/list-files/");
        if (!response.ok) {
          throw new Error("Failed to fetch files");
        }
        const files = await response.json();
        setUploadedFiles(
          files.map((file: FileResponse) => ({
            id: Math.random().toString(36).substr(2, 9),
            name: file.name,
            size: file.size,
          }))
        );
      } catch (error) {
        console.error("Error fetching initial files:", error);
      }
    };

    fetchInitialFiles();
  }, []);

  const handleClearContext = async () => {
    try {
      setIsProcessing(true);
      const response = await fetch(
        "http://localhost:8000/api/clear-documents/",
        {
          method: "POST",
        }
      );

      if (!response.ok) {
        throw new Error("Failed to clear documents");
      }

      alert("Documents collection cleared successfully");
    } catch (error) {
      console.error("Error clearing documents:", error);
      alert("Failed to clear documents");
    } finally {
      setIsProcessing(false);
    }
  };

  const handleIngestFiles = async () => {
    if (uploadedFiles.length === 0) {
      alert("No files to ingest");
      return;
    }

    try {
      setIsProcessing(true);
      const response = await fetch(
        "http://localhost:8000/api/ingest-documents/",
        {
          method: "POST",
        }
      );

      if (!response.ok) {
        throw new Error("Failed to ingest documents");
      }

      alert("Files ingested successfully");
    } catch (error) {
      console.error("Error ingesting files:", error);
      alert("Failed to ingest files");
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const uploadFile = async (file: File) => {
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://localhost:8000/api/upload/", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Upload failed");
      }

      const data = await response.json();
      setUploadStatus((prev) => ({ ...prev, [file.name]: "success" }));
      return data;
    } catch (error) {
      setUploadStatus((prev) => ({ ...prev, [file.name]: "error" }));
      console.error("Error uploading file:", error);
      throw error;
    }
  };

  const handleDrop = useCallback(async (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
  }, []);

  const handleFileInput = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      if (e.target.files) {
        const files = Array.from(e.target.files);
        handleFiles(files);
      }
    },
    []
  );

  const handleFiles = async (files: File[]) => {
    const newFiles = files.map((file) => ({
      id: Math.random().toString(36).substr(2, 9),
      name: file.name,
      size: file.size,
    }));
    setUploadedFiles((prev) => [...prev, ...newFiles]);

    // Upload each file
    for (const file of files) {
      try {
        await uploadFile(file);
      } catch (error) {
        console.error(`Failed to upload ${file.name}:`, error);
      }
    }
  };

  return (
    <div className="flex flex-col h-full gap-5">
      <div className="h-1/2 bg-[#1a1a1a] rounded-lg p-4 min-h-[100px]">
        <h3 className="mt-0 mb-2.5">Uploaded Files</h3>
        {uploadedFiles.length === 0 ? (
          <p>No files uploaded yet</p>
        ) : (
          <ul className="list-none p-0 m-0">
            {uploadedFiles.map((file) => (
              <li
                key={file.id}
                className="py-1.5 border-b border-[#333] flex justify-between items-center last:border-b-0"
              >
                {file.name} ({(file.size / 1024).toFixed(2)} KB)
                {uploadStatus[file.name] === "success" && (
                  <span className="text-[#4caf50] ml-2.5">✓</span>
                )}
                {uploadStatus[file.name] === "error" && (
                  <span className="text-[#f44336] ml-2.5">✗</span>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>

      <div
        className={`flex-1 border-2 border-dashed rounded-lg flex flex-col items-center justify-center p-5 bg-[#1a1a1a] transition-all duration-300 ${
          isDragging ? "border-[#535bf2] bg-[#242424]" : "border-[#646cff]"
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <p className="my-1">Drag and drop files here</p>
        <p>or</p>
        <input
          type="file"
          id="file-input"
          multiple
          onChange={handleFileInput}
          className="hidden"
        />
        <button
          onClick={() => document.getElementById("file-input")?.click()}
          className="mt-2.5 bg-[#646cff] text-white px-4 py-2 rounded hover:bg-[#535bf2]"
        >
          Choose Files
        </button>
      </div>
      <div className="h-[200px] flex flex-col gap-2.5 p-4 bg-[#1a1a1a] rounded-lg">
        <button
          className="flex-1 p-2.5 border-none rounded text-base cursor-pointer transition-colors duration-300 bg-[#f44336] text-white hover:bg-[#d32f2f] disabled:opacity-50"
          onClick={handleClearContext}
          disabled={isProcessing}
        >
          {isProcessing ? "Processing..." : "Clear context"}
        </button>
        <button
          className="flex-1 p-2.5 border-none rounded text-base cursor-pointer transition-colors duration-300 bg-[#4caf50] text-white hover:bg-[#388e3c] disabled:opacity-50"
          onClick={handleIngestFiles}
          disabled={isProcessing}
        >
          {isProcessing ? "Processing..." : "Ingest files"}
        </button>
      </div>
    </div>
  );
}

export default FileUpload;
