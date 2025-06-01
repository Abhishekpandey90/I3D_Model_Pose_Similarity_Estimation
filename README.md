# I3D Model Pose Similarity Estimation

This project is built to evaluate human pose similarity from video sequences using the Inflated 3D ConvNet (I3D) deep learning architecture. It compares a user's action video against a reference video (e.g., a trainer's performance) to determine similarity scores, making it useful for fitness coaching, physical therapy, and skill assessment applications.

## 📌 Key Features

- 🎥 Full video-based pose similarity comparison using the I3D model
- 🧠 Deep learning backend with action recognition capabilities
- ⚙️ FastAPI-powered RESTful API for inference
- 🔐 JWT-based user authentication system
- 📦 Modular structure for easy maintenance and extension
- 💾 SQLite database for managing user or session data
- 📁 Organized backup and legacy code

---

## 📁 Project Structure

```
├── auth.py                    # Token and authentication utilities
├── database.py                # SQLite connection and schema handling
├── i3d_server.py              # Main FastAPI server with inference endpoint
├── jwt_token_gen.py           # JWT token creation
├── pydantic_schema.py         # Request and response models
├── requirements.txt           # Required Python packages
├── test.py                    # Script for quick testing
├── video_process.py           # Handles frame extraction and preprocessing
├── coach_data.db              # SQLite database file
├── backups/                   # Backup versions of scripts
├── old/                       # Legacy scripts for reference
└── README.md                  # Project documentation
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip package manager
- FFmpeg (for advanced video processing, optional)

### 1. Clone the Repository

```bash
git clone https://github.com/Abhishekpandey90/I3D_Model_Pose_Similarity_Estimation.git
cd I3D_Model_Pose_Similarity_Estimation
```

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv venv
venv\Scripts\activate    # On Windows
# Or:
source venv/bin/activate   # On macOS/Linux
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the FastAPI Server

```bash
uvicorn i3d_server:app --reload
```

Then open your browser at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)  
You’ll see Swagger UI for testing the API.

---

## 📦 API Endpoints (via FastAPI)

| Method | Endpoint           | Description                          |
|--------|--------------------|--------------------------------------|
| POST   | `/predict`         | Compare input video with reference   |
| POST   | `/token`           | Get access token (JWT)               |
| GET    | `/healthcheck`     | Basic server health check            |

---

## 🧠 Model Details

The model uses an Inflated 3D ConvNet (I3D) pretrained on action recognition datasets (e.g., Kinetics-400) to extract spatiotemporal features from videos. Cosine similarity or distance metrics are then used to measure similarity between embeddings of reference and user videos.

---

## 🧪 Testing

You can run:

```bash
python test.py
```

Or directly test via Swagger UI.

---

## ✅ Dependencies

Listed in `requirements.txt`. Common packages include:

- fastapi
- uvicorn
- opencv-python
- numpy
- pydantic
- python-jose
- sqlite3
- torch or tensorflow (depending on model version)

---

## 🙋‍♂️ Author

**Abhishek Pandey**  
B.Tech in AI & ML  
GitHub: [Abhishekpandey90](https://github.com/Abhishekpandey90)

---

## 📌 To Do (Future Enhancements)

- Deploy the API to Render or Hugging Face Spaces
- Replace I3D with more lightweight model (e.g., MoViNet, SlowFast)
- Add user dashboard for visual feedback
- Add frontend for uploading videos and displaying similarity score

---

## 🛡️ License

This project is licensed under the MIT License - see the LICENSE file for details.
