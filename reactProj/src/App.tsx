import React, { useState, ChangeEvent, FormEvent } from "react";

const App: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [classification, setClassification] = useState<string>("");
  const [croppedImageUrl, setCroppedImageUrl] = useState<string>("");

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    //State variables themselves are read-only and should not be modified directly. To update state values, you use the provided updater functions
    if (event.target.files && event.target.files.length > 0) {
      setSelectedFile(event.target.files[0]);
      setClassification(""); // Clear the previous classification
      setCroppedImageUrl(""); // Clear the previous cropped image
    }
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    //async : excuted independently (not sync : in the flow) it interrupt
    event.preventDefault();
    if (!selectedFile) {
      alert("Please select a file first!");
      return;
    }

    const formData = new FormData(); //handle file upload
    formData.append("file", selectedFile);

    try {
      const response = await fetch("http://127.0.0.1:5000/classify", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      const data = await response.json();
      setClassification(data.classification);
      if (data.cropped_image_url) {
        setCroppedImageUrl(data.cropped_image_url);
      } else {
        setCroppedImageUrl(""); // Ensure cropped image is cleared if not returned
      }
    } catch (error) {
      console.error("There was a problem with the fetch operation:", error);
    }
  };

  return (
    <div>
      <h1>Image Classification and Cropping </h1>
      <form onSubmit={handleSubmit}>
        <input type="file" onChange={handleFileChange} />
        <button className="btn btn-primary" type="submit">
          Classify Image
        </button>
      </form>
      {classification && (
        <div>
          <h2>Classification: {classification}</h2>
          {croppedImageUrl && (
            <div>
              <h3>Cropped Document Image:</h3>
              <img src={croppedImageUrl} alt="Cropped result" />
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default App;
