import React, { useState } from 'react';
import '../styles/CaptionPopup.css';

function CaptionPopup({ onClose, onSubmitCaption }) {
  const [caption, setCaption] = useState('');

  const handleChange = (e) => {
    setCaption(e.target.value);
  };

  const handleSubmit = () => {
    if (caption.trim() !== '') {
      console.log("Submitted caption:", caption);
      onSubmitCaption(caption.trim()); // Pass the caption up
      onClose(); // Close the pop-up after submission
    } else {
      alert("Please enter a caption before submitting.");
    }
  };

  return (
    <div className="popup-overlay" onClick={onClose}>
      <div className="popup-box" onClick={(e) => e.stopPropagation()}>
        <h2>Submit Caption</h2>
        <textarea
          value={caption}
          onChange={handleChange}
          placeholder="Type your caption here..."
        ></textarea>
        <div className="popup-buttons">
          <button onClick={handleSubmit}>Submit</button>
          <button onClick={onClose}>Cancel</button>
        </div>
      </div>
    </div>
  );
}

export default CaptionPopup;