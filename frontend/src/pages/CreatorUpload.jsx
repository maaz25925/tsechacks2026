import React, { useState } from 'react';
import { Upload as UploadIcon, Video, Plus, Sparkles, Image as ImageIcon, FileText, X } from 'lucide-react';
import { useAuth } from '../features/auth/AuthProvider.jsx';
import './CreatorUpload.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export default function CreatorUpload() {
  const { user } = useAuth();
  const [currentStep, setCurrentStep] = useState(1);
  const [contentType, setContentType] = useState('single');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [form, setForm] = useState({
    title: '',
    description: '',
    category: 'Web Development',
    tags: [],
    videoFile: null,
    thumbnail: null,
    baseCoursePrice: '',
    visibility: 'draft',
    termsAccepted: false,
    additionalResources: [],
  });
  const [sections, setSections] = useState([]);
  const [currentTag, setCurrentTag] = useState('');

  const steps = [
    { id: 1, name: 'Basic Info', description: 'Title, description & category' },
    { id: 2, name: 'Content', description: 'Videos & thumbnail' },
    { id: 3, name: 'Pricing & Extras', description: 'Price & resources' },
    { id: 4, name: 'Review', description: 'Finalize & submit' },
  ];

  const nextStep = () => {
    if (currentStep < 4) setCurrentStep(currentStep + 1);
  };

  const prevStep = () => {
    if (currentStep > 1) setCurrentStep(currentStep - 1);
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm((prev) => ({ ...prev, [name]: type === 'checkbox' ? checked : value }));
  };

  const handleFileChange = (e) => {
    setForm((prev) => ({ ...prev, videoFile: e.target.files[0] }));
  };

  const handleThumbnailChange = (e) => {
    setForm((prev) => ({ ...prev, thumbnail: e.target.files[0] }));
  };

  const handleResourceUpload = (e) => {
    const files = Array.from(e.target.files);
    setForm((prev) => ({
      ...prev,
      additionalResources: [...prev.additionalResources, ...files]
    }));
  };

  const removeResource = (index) => {
    setForm((prev) => ({
      ...prev,
      additionalResources: prev.additionalResources.filter((_, i) => i !== index)
    }));
  };

  const addTag = () => {
    if (currentTag.trim() && !form.tags.includes(currentTag.trim())) {
      setForm((prev) => ({ ...prev, tags: [...prev.tags, currentTag.trim()] }));
      setCurrentTag('');
    }
  };

  const removeTag = (tagToRemove) => {
    setForm((prev) => ({ ...prev, tags: prev.tags.filter(tag => tag !== tagToRemove) }));
  };

  const suggestTitles = () => {
    const suggestions = [
      'Master ' + form.category + ' in 30 Days',
      'Complete ' + form.category + ' Bootcamp 2026',
      form.category + ': From Zero to Hero'
    ];
    const suggestion = suggestions[Math.floor(Math.random() * suggestions.length)];
    setForm((prev) => ({ ...prev, title: suggestion }));
  };

  const generateDescription = () => {
    const generated = `Learn ${form.category} from scratch in this comprehensive course. Perfect for beginners and intermediate learners. You'll master key concepts, build real-world projects, and gain the skills needed to succeed.\n\nWhat you'll learn:\n- Core fundamentals\n- Advanced techniques\n- Industry best practices\n\nPrerequisites:\n- Basic computer skills\n- Passion to learn`;
    setForm((prev) => ({ ...prev, description: generated }));
  };

  const suggestTags = () => {
    const categoryTags = {
      'Web Development': ['javascript', 'react', 'frontend', 'css', 'html'],
      'Data Science': ['python', 'machine-learning', 'data-analysis', 'statistics'],
      'Design': ['ui-ux', 'figma', 'prototyping', 'visual-design'],
      'Backend': ['nodejs', 'api', 'database', 'server'],
      'AI/ML': ['artificial-intelligence', 'neural-networks', 'tensorflow', 'deep-learning'],
      'DevOps': ['docker', 'kubernetes', 'ci-cd', 'cloud']
    };
    const suggestions = categoryTags[form.category] || ['beginner', 'tutorial', 'course'];
    setForm((prev) => ({ ...prev, tags: [...new Set([...prev.tags, ...suggestions.slice(0, 3)])] }));
  };

  const addSection = () => {
    setSections([...sections, { title: '', description: '', videoFile: null }]);
  };

  const updateSection = (index, field, value) => {
    const updated = [...sections];
    updated[index][field] = value;
    setSections(updated);
  };

  const removeSection = (index) => {
    setSections(sections.filter((_, i) => i !== index));
  };

  const uploadContent = async () => {
    setIsUploading(true);
    setUploadProgress(0);

    try {
      // Validate required fields
      if (!form.title || !form.description || !form.category || !form.baseCoursePrice) {
        alert('Please fill in all required fields');
        return;
      }

      if (!form.thumbnail) {
        alert('Please upload a thumbnail image');
        return;
      }

      // For single video, check if video file exists
      if (contentType === 'single' && !form.videoFile) {
        alert('Please upload a video file');
        return;
      }

      // For course, check if sections have videos
      if (contentType === 'course' && sections.length === 0) {
        alert('Please add at least one section with a video');
        return;
      }

      // Create FormData
      const formData = new FormData();

      // Check file sizes
      const maxFileSize = 100 * 1024 * 1024; // 100MB
      if (contentType === 'single' && form.videoFile) {
        if (form.videoFile.size > maxFileSize) {
          console.warn(`Video file is large: ${(form.videoFile.size / 1024 / 1024).toFixed(2)}MB`);
          if (!confirm(`Video file is ${(form.videoFile.size / 1024 / 1024).toFixed(2)}MB. This may take a while to upload. Continue?`)) {
            return;
          }
        }
      }
      if (form.thumbnail && form.thumbnail.size > 10 * 1024 * 1024) {
        alert('Thumbnail file is too large. Please use an image under 10MB.');
        return;
      }

      // Add required fields according to FastAPI endpoint
      formData.append('title', form.title);
      formData.append('description', form.description);
      formData.append('category', form.category);
      formData.append('visibility', form.visibility);
      formData.append('basePrice', parseFloat(form.baseCoursePrice));
      formData.append('tags_json', JSON.stringify(form.tags));

      // Add video file(s)
      if (contentType === 'single' && form.videoFile) {
        // For single video, append once
        formData.append('video', form.videoFile);
      } else if (contentType === 'course') {
        // For multi-video course, append each section's video with the same field name
        sections.forEach((section) => {
          if (section.videoFile) {
            formData.append('video', section.videoFile);
          }
        });
      }

      // Add thumbnail (required)
      formData.append('thumbnail', form.thumbnail);

      // Get auth token from localStorage
      const token = localStorage.getItem('access_token');
      if (!token) {
        alert('You must be logged in to upload content');
        return;
      }

      // Test backend connectivity first
      try {
        const healthCheck = await fetch(`${API_BASE_URL}/health`, {
          method: 'GET',
        });
        if (!healthCheck.ok) {
          throw new Error('Backend health check failed');
        }
      } catch (healthError) {
        alert('Cannot connect to backend server. Please ensure the backend is running on http://localhost:8000');
        return;
      }

      // Make API call with timeout
      setUploadProgress(30);

      // Create abort controller for timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => {
        controller.abort();
      }, 120000); // 2 minute timeout

      try {
        const response = await fetch(`${API_BASE_URL}/creator/upload`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            // DO NOT set Content-Type - let browser set it with boundary for multipart/form-data
          },
          body: formData,
          signal: controller.signal,
        });

        clearTimeout(timeoutId);
        setUploadProgress(80);

        console.log('Response status:', response.status);
        console.log('Response headers:', Object.fromEntries(response.headers.entries()));

        if (!response.ok) {
          let errorMessage = 'Upload failed';
          try {
            const errorData = await response.json();
            console.error('API Error Response:', errorData);
            errorMessage = errorData.detail || errorData.error?.message || JSON.stringify(errorData);
          } catch (e) {
            errorMessage = `Upload failed with status ${response.status}: ${response.statusText}`;
          }
          throw new Error(errorMessage);
        }

        const result = await response.json();
        setUploadProgress(100);

        console.log('Upload successful:', result);
        alert(`Content uploaded successfully! Listing ID: ${result.listing_id}`);

        // Reset form
        setForm({
          title: '',
          description: '',
          category: 'Web Development',
          tags: [],
          videoFile: null,
          thumbnail: null,
          baseCoursePrice: '',
          visibility: 'draft',
          termsAccepted: false,
          additionalResources: [],
        });
        setSections([]);
        setCurrentStep(1);
      } catch (fetchError) {
        clearTimeout(timeoutId);
        if (fetchError.name === 'AbortError') {
          throw new Error('Upload timeout - file may be too large or connection is slow');
        }
        throw fetchError;
      }

    } catch (error) {
      console.error('Upload error:', error);
      alert(`Upload failed: ${error.message || 'Unknown error occurred'}`);
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (currentStep < 4) {
      nextStep();
    } else {
      uploadContent();
    }
  };

  return (
    <div className="creator-upload-container">
      <div className="creator-upload">
        <h1>Upload Your Content</h1>
        <p className="subtitle">Share your knowledge and earn from every student</p>

        {/* Stepper */}
        <div className="stepper">
          {steps.map((step, index) => (
            <React.Fragment key={step.id}>
              <div className="step-item">
                <div
                  className={`step-circle ${currentStep >= step.id ? 'active' : ''} ${currentStep > step.id ? 'completed' : ''}`}
                >
                  {currentStep > step.id ? '✓' : step.id}
                </div>
                <div className="step-label">
                  <span className="step-name">{step.name}</span>
                  <span className="step-description">{step.description}</span>
                </div>
              </div>
              {index < steps.length - 1 && (
                <div className={`step-line ${currentStep > step.id ? 'completed' : ''}`}></div>
              )}
            </React.Fragment>
          ))}
        </div>

        <form onSubmit={handleSubmit} className="upload-form">
          {/* Step 1: Basic Info */}
          {currentStep === 1 && (
            <div className="form-step">
              <h2 className="step-title">Basic Information</h2>

              <div className="form-group">
                <label>Content Type <span className="required-star">*</span></label>
                <div className="type-toggle">
                  <button
                    type="button"
                    className={`toggle-btn ${contentType === 'single' ? 'active' : ''}`}
                    onClick={() => setContentType('single')}
                  >
                    Single Video Session
                  </button>
                  <button
                    type="button"
                    className={`toggle-btn ${contentType === 'course' ? 'active' : ''}`}
                    onClick={() => setContentType('course')}
                  >
                    Multi-Video Course
                  </button>
                </div>
              </div>

              <div className="form-group">
                <label>Title <span className="required-star">*</span></label>
                <div className="input-with-ai">
                  <input
                    type="text"
                    name="title"
                    value={form.title}
                    onChange={handleChange}
                    placeholder="Enter course title"
                    maxLength={100}
                    required
                  />
                  <button type="button" className="ai-btn" onClick={suggestTitles}>
                    <Sparkles size={16} />
                    Suggest Titles
                  </button>
                </div>
                <span className="char-count">{form.title.length}/100</span>
              </div>

              <div className="form-group">
                <label>Description <span className="required-star">*</span></label>
                <div className="input-with-ai">
                  <textarea
                    name="description"
                    value={form.description}
                    onChange={handleChange}
                    placeholder="What will students learn? Include prerequisites and outcomes"
                    rows="6"
                    maxLength={5000}
                    required
                  />
                  <button type="button" className="ai-btn" onClick={generateDescription}>
                    <Sparkles size={16} />
                    Generate Description
                  </button>
                </div>
                <span className="char-count">{form.description.length}/5000</span>
              </div>

              <div className="form-group">
                <label>Tags/Keywords</label>
                <div className="input-with-ai">
                  <div className="tag-input-wrapper">
                    <input
                      type="text"
                      value={currentTag}
                      onChange={(e) => setCurrentTag(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
                      placeholder="Add tags (press Enter)"
                    />
                    <button type="button" className="add-tag-btn" onClick={addTag}>
                      <Plus size={16} />
                    </button>
                  </div>
                  <button type="button" className="ai-btn" onClick={suggestTags}>
                    <Sparkles size={16} />
                    Suggest Tags
                  </button>
                </div>
                {form.tags.length > 0 && (
                  <div className="tags-list">
                    {form.tags.map((tag, index) => (
                      <span key={index} className="tag-chip">
                        {tag}
                        <button type="button" onClick={() => removeTag(tag)}>
                          <X size={14} />
                        </button>
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Step 2: Content */}
          {currentStep === 2 && (
            <div className="form-step">
              <h2 className="step-title">Upload Content</h2>

              <div className="form-row">
                <div className="form-group">
                  <label>Category <span className="required-star">*</span></label>
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
                  <label>Visibility <span className="required-star">*</span></label>
                  <select
                    name="visibility"
                    value={form.visibility}
                    onChange={handleChange}
                  >
                    <option value="draft">Draft</option>
                    <option value="private">Private</option>
                    <option value="public">Public</option>
                  </select>
                </div>
              </div>

              {contentType === 'single' && (
                <div className="form-group">
                  <label>Video File <span className="required-star">*</span></label>
                  <div className="file-upload">
                    <Video size={32} />
                    <div>
                      <p>Drag and drop or click to upload (MP4, max 2GB)</p>
                    </div>
                    <input
                      type="file"
                      accept="video/mp4,video/webm"
                      onChange={handleFileChange}
                      required={contentType === 'single'}
                    />
                  </div>
                  {form.videoFile && (
                    <p className="file-name">✓ {form.videoFile.name}</p>
                  )}
                </div>
              )}

              {contentType === 'course' && (
                <div className="form-group">
                  <div className="section-header">
                    <label>Course Sections</label>
                    <button type="button" className="add-section-btn" onClick={addSection}>
                      <Plus size={16} />
                      Add Section
                    </button>
                  </div>
                  {sections.map((section, index) => (
                    <div key={index} className="course-section">
                      <div className="section-title-row">
                        <h4>Section {index + 1}</h4>
                        <button type="button" className="remove-btn" onClick={() => removeSection(index)}>
                          <X size={16} />
                        </button>
                      </div>
                      <input
                        type="text"
                        placeholder="Section title"
                        value={section.title}
                        onChange={(e) => updateSection(index, 'title', e.target.value)}
                        required
                      />
                      <textarea
                        placeholder="Description (optional)"
                        value={section.description}
                        onChange={(e) => updateSection(index, 'description', e.target.value)}
                        rows="2"
                      />
                      <div className="file-upload small">
                        <Video size={24} />
                        <p>Upload video</p>
                        <input
                          type="file"
                          accept="video/mp4,video/webm"
                          onChange={(e) => updateSection(index, 'videoFile', e.target.files[0])}
                        />
                      </div>
                      {section.videoFile && (
                        <p className="file-name">✓ {section.videoFile.name}</p>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Step 3: Pricing & Extras */}
          {currentStep === 3 && (
            <div className="form-step">
              <h2 className="step-title">Pricing & Additional Resources</h2>

              <div className="form-group">
                <label>Thumbnail <span className="required-star">*</span></label>
                <div className="file-upload">
                  <ImageIcon size={32} />
                  <div>
                    <p>Upload thumbnail (1280x720 recommended)</p>
                  </div>
                  <input
                    type="file"
                    accept="image/jpeg,image/png"
                    onChange={handleThumbnailChange}
                  />
                </div>
                {form.thumbnail && (
                  <div className="thumbnail-preview">
                    <img src={URL.createObjectURL(form.thumbnail)} alt="Thumbnail preview" />
                  </div>
                )}
              </div>

              <div className="form-group">
                <label>Base Course Price (USD) <span className="required-star">*</span></label>
                <input
                  type="number"
                  name="baseCoursePrice"
                  value={form.baseCoursePrice}
                  onChange={handleChange}
                  placeholder="e.g., 20"
                  min="0"
                  step="0.01"
                  required
                />
              </div>

              <div className="form-group">
                <label>Additional Resources <span className="char-limit">(Optional)</span></label>
                <div className="file-upload">
                  <FileText size={32} />
                  <div>
                    <p>Upload PDFs, documents, or learning materials</p>
                  </div>
                  <input
                    type="file"
                    accept=".pdf,.doc,.docx,.txt"
                    multiple
                    onChange={handleResourceUpload}
                  />
                </div>
                {form.additionalResources.length > 0 && (
                  <div className="resources-list">
                    {form.additionalResources.map((resource, index) => (
                      <div key={index} className="resource-item">
                        <FileText size={16} />
                        <span>{resource.name}</span>
                        <button type="button" onClick={() => removeResource(index)}>
                          <X size={14} />
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Step 4: Review */}
          {currentStep === 4 && (
            <div className="form-step">
              <h2 className="step-title">Review & Submit</h2>

              <div className="review-section">
                <h3>Content Summary</h3>
                <div className="review-item">
                  <span className="review-label">Type:</span>
                  <span className="review-value">{contentType === 'single' ? 'Single Video Session' : 'Multi-Video Course'}</span>
                </div>
                <div className="review-item">
                  <span className="review-label">Title:</span>
                  <span className="review-value">{form.title || 'Not provided'}</span>
                </div>
                <div className="review-item">
                  <span className="review-label">Category:</span>
                  <span className="review-value">{form.category}</span>
                </div>
                <div className="review-item">
                  <span className="review-label">Price:</span>
                  <span className="review-value">${form.baseCoursePrice || '0'}</span>
                </div>
                <div className="review-item">
                  <span className="review-label">Visibility:</span>
                  <span className="review-value">{form.visibility}</span>
                </div>
                {contentType === 'course' && sections.length > 0 && (
                  <div className="review-item">
                    <span className="review-label">Sections:</span>
                    <span className="review-value">{sections.length} section(s)</span>
                  </div>
                )}
              </div>

              <div className="form-group">
                <div className="checkbox-group">
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      name="termsAccepted"
                      checked={form.termsAccepted}
                      onChange={handleChange}
                      required
                    />
                    <span>I accept the Terms and Conditions <span className="required-star">*</span></span>
                  </label>
                </div>
              </div>
            </div>
          )}

          {/* Navigation Buttons */}
          <div className="form-navigation">
            {currentStep > 1 && (
              <button type="button" className="nav-btn prev-btn" onClick={prevStep}>
                ← Previous
              </button>
            )}
            {currentStep < 4 ? (
              <button type="button" className="nav-btn next-btn" onClick={nextStep}>
                Next →
              </button>
            ) : (
              <button type="submit" className="submit-btn" disabled={isUploading}>
                <UploadIcon size={20} />
                {isUploading
                  ? `Uploading... ${uploadProgress}%`
                  : `Submit ${contentType === 'single' ? 'Session' : 'Course'}`
                }
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}
