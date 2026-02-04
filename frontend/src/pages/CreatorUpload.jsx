import { useState } from 'react';
import { Upload as UploadIcon, Video } from 'lucide-react';
import './CreatorUpload.css';

export default function CreatorUpload() {
  const [form, setForm] = useState({
    title: '',
    description: '',
    category: 'Web Development',
    pricePerMinute: '0.5',
    videoFile: null,
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleFileChange = (e) => {
    setForm((prev) => ({ ...prev, videoFile: e.target.files[0] }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Uploading:', form);
    alert('Course uploaded successfully!');
  };

  return (
    <div className="creator-upload">
      <h1>Upload Your Course</h1>
      <p className="subtitle">Share your knowledge and earn from every student</p>

      <form onSubmit={handleSubmit} className="upload-form">
        <div className="form-group">
          <label>Course Title *</label>
          <input
            type="text"
            name="title"
            value={form.title}
            onChange={handleChange}
            placeholder="e.g., Advanced React Patterns"
            required
          />
        </div>

        <div className="form-group">
          <label>Description *</label>
          <textarea
            name="description"
            value={form.description}
            onChange={handleChange}
            placeholder="Describe your course..."
            rows="4"
            required
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Category *</label>
            <select
              name="category"
              value={form.category}
              onChange={handleChange}
            >
              <option>Web Development</option>
              <option>Data Science</option>
              <option>Design</option>
              <option>Backend</option>
              <option>AI/ML</option>
              <option>DevOps</option>
            </select>
          </div>

          <div className="form-group">
            <label>Price Per Minute (USD) *</label>
            <input
              type="number"
              name="pricePerMinute"
              value={form.pricePerMinute}
              onChange={handleChange}
              min="0.1"
              step="0.1"
              required
            />
          </div>
        </div>

        <div className="form-group">
          <label>Video File *</label>
          <div className="file-upload">
            <Video size={32} />
            <div>
              <p>Drag and drop your video here, or click to select</p>
              <p className="file-hint">
                Supported formats: MP4, WebM, Ogg (Max 2GB)
              </p>
            </div>
            <input
              type="file"
              accept="video/*"
              onChange={handleFileChange}
              required
            />
          </div>
          {form.videoFile && (
            <p className="file-name">✓ {form.videoFile.name}</p>
          )}
        </div>

        <button type="submit" className="submit-btn">
          <UploadIcon size={20} />
          Upload Course
        </button>
      </form>
    </div>
  );
}
