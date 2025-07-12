# NeuroLearn - AI-Powered Adaptive Smart Classroom

## Overview

NeuroLearn is an advanced adaptive learning platform designed to personalize education using artificial intelligence. The system leverages Intel's OpenVINO toolkit for efficient AI inference, enabling real-time analysis of student learning patterns, prediction of performance, and dynamic content optimization. NeuroLearn aims to address the limitations of traditional, one-size-fits-all education by providing tailored learning experiences for students of all backgrounds and abilities.

## Problem Statement

Conventional classrooms often fail to accommodate diverse learning paces, disabilities, and socio-economic barriers. Students with learning difficulties or those from underserved regions may fall behind due to a lack of personalized support. NeuroLearn addresses these challenges by using AI to adapt content and teaching strategies to each student's unique needs.

## Key Features

### AI-Powered Learning Analysis
- **OpenVINO Integration**: Utilizes Intel's OpenVINO for high-performance, hardware-accelerated AI inference.
- **Learning Style Detection**: Identifies visual, auditory, and kinesthetic learning preferences from student interaction data.
- **Pattern Recognition**: Analyzes engagement, accuracy, and behavioral trends to inform adaptive strategies.
- **Real-Time Adaptation**: Adjusts content difficulty and presentation on-the-fly based on AI insights.

### Adaptive Content Delivery
- **Personalized Difficulty**: Dynamically modifies question complexity to match student ability.
- **Multi-Modal Learning**: Supports a range of learning styles with visual, auditory, and hands-on content.
- **Progress Tracking**: Monitors student engagement and performance in real time.
- **Smart Recommendations**: Provides actionable suggestions for both students and educators.

### Comprehensive Analytics
- **Progress Visualization**: Interactive dashboards and charts display individual and group learning trajectories.
- **Performance Metrics**: Detailed analysis of accuracy, improvement rates, and engagement.
- **Predictive Insights**: AI-driven forecasts of future performance and learning needs.

## Technology Stack

- **Backend**: Python Flask
- **AI/ML**: OpenVINO, scikit-learn, NumPy, Pandas
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5
- **Visualization**: Matplotlib, Seaborn
- **Database**: SQLite (for demo; can be replaced with production DB)

## OpenVINO Integration

NeuroLearn uses OpenVINO for all core AI/ML features:

- **Learning Pattern Analysis**: Neural network models analyze student interaction data to determine dominant learning styles.
- **Performance Prediction**: Time series models forecast student progress and identify potential challenges.
- **Content Optimization**: AI-driven recommendation systems suggest optimal content types and difficulty adjustments.
- **Device Detection**: Automatically detects and utilizes available hardware (CPU, GPU, Intel Neural Compute Stick).
- **Performance Benchmarking**: Measures inference speed and throughput for real-time analytics.
- **Model Status Monitoring**: Provides live status of all OpenVINO models and devices.

### API Endpoints

- `GET /api/openvino/status` - Returns OpenVINO system and model status.
- `GET /api/openvino/benchmark` - Returns OpenVINO performance metrics.
- `POST /api/openvino/analyze_learning_style` - Analyzes learning style using OpenVINO.
- `POST /api/openvino/predict_performance` - Predicts performance using OpenVINO.
- `POST /api/openvino/optimize_content` - Optimizes content delivery using OpenVINO.
- `GET /api/openvino/demo` - Runs a comprehensive OpenVINO demo.

### Fallback System

If OpenVINO is unavailable, the system automatically falls back to simulated analysis using scikit-learn and traditional rule-based algorithms, ensuring uninterrupted functionality.

## Application Architecture

- **openvino_utils.py**: Contains the `OpenVINOLearningAnalyzer` class, which manages model initialization, inference, device detection, and benchmarking.
- **app.py**: Main Flask application. Integrates the OpenVINO analyzer into the adaptive learning engine and exposes all API endpoints.
- **templates/**: HTML templates for the web interface, including dashboards, analytics, and settings.
- **static/**: Static assets (JavaScript, CSS, uploads).
- **requirements.txt**: Python dependencies, including OpenVINO.

## Setup and Installation

### Prerequisites

- **Python 3.8 or higher** (recommended: Python 3.9+)
- **pip package manager**
- **Intel OpenVINO toolkit** (version 2023.2.0 or compatible)
- **Git** (for cloning the repository)
- **Web browser** (Chrome, Firefox, Safari, Edge)

### System Requirements

- **RAM**: Minimum 4GB, recommended 8GB+
- **Storage**: At least 2GB free space
- **CPU**: Multi-core processor (Intel/AMD)
- **GPU**: Optional but recommended for better OpenVINO performance
- **OS**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)

### Installation Steps

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd "AI intel"
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify OpenVINO installation**:
   ```bash
   python -c "import openvino; print('OpenVINO version:', openvino.__version__)"
   ```

5. **Initialize the database** (automatic on first run):
   ```bash
   python app.py
   ```

6. **Access the application**:
   Open your browser and navigate to `http://localhost:5000`

### Configuration

#### Environment Variables (Optional)

Create a `.env` file in the project root for custom configuration:

```bash
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here

# Database Configuration
DATABASE_URL=sqlite:///adaptive_learning.db

# OpenVINO Configuration
OPENVINO_DEVICE=CPU
OPENVINO_MODEL_PATH=models/intel/

# Server Configuration
HOST=0.0.0.0
PORT=5000
```

#### Database Initialization

The application automatically initializes the SQLite database on first run. The database file (`adaptive_learning.db`) will be created in the project root with the following tables:

- `students`: Student profiles and learning preferences
- `sessions`: Learning session data and performance metrics
- `questions`: Question bank for different subjects and difficulty levels

#### OpenVINO Model Initialization

On first startup, the system will:

1. **Detect available devices** (CPU, GPU, MYRIAD)
2. **Create neural network models** for:
   - Learning pattern analysis (10 input features → 3 learning styles)
   - Performance prediction (5 historical data points → 1 prediction)
   - Content optimization (4 input features → 3 optimization parameters)
3. **Compile models** for the detected device
4. **Run initial benchmarks** to verify performance

### Verification Steps

After installation, verify the setup:

1. **Check OpenVINO status**:
   ```bash
   curl http://localhost:5000/api/openvino/status
   ```

2. **Run OpenVINO demo**:
   ```bash
   curl http://localhost:5000/api/openvino/demo
   ```

3. **Test learning analysis**:
   ```bash
   curl -X POST http://localhost:5000/api/openvino/analyze_learning_style \
     -H "Content-Type: application/json" \
     -d '{"interaction_data": [0.8, 0.6, 0.4, 0.7, 0.5, 0.3, 0.9, 0.2, 0.6, 0.8]}'
   ```

### Troubleshooting

#### Common Issues

1. **OpenVINO not found**:
   ```bash
   pip install openvino==2023.2.0
   ```

2. **Port 5000 already in use**:
   ```bash
   # On macOS, disable AirPlay Receiver in System Preferences
   # Or change the port in app.py
   ```

3. **Database initialization errors**:
   ```bash
   # Delete the database file and restart
   rm adaptive_learning.db
   python app.py
   ```

4. **OpenVINO model creation fails**:
   ```bash
   # Check available devices
   python -c "from openvino.runtime import Core; print(Core().available_devices)"
   ```

#### Performance Optimization

1. **For better OpenVINO performance**:
   - Use a GPU if available
   - Ensure sufficient RAM (8GB+ recommended)
   - Close unnecessary applications

2. **For production deployment**:
   - Use a WSGI server (Gunicorn, uWSGI)
   - Configure environment variables
   - Set up proper logging
   - Use a production database (PostgreSQL, MySQL)

## Usage

### Starting the Application

1. **Activate virtual environment** (if using one):
   ```bash
   source venv/bin/activate  # macOS/Linux
   # or
   venv\Scripts\activate     # Windows
   ```

2. **Run the application**:
   ```bash
   python app.py
   ```

3. **Access the web interface**:
   Open `http://localhost:5000` in your browser

### Using the Application

#### For Students

1. **Start a Learning Session**:
   - Enter a student ID (e.g., "STU001")
   - Select a subject (Math, Science, English)
   - Choose difficulty level (Easy, Medium, Hard)
   - Click "Start Learning Session"

2. **Complete Questions**:
   - Answer questions based on your learning style
   - The system adapts difficulty and content type
   - View real-time feedback and progress

3. **View Progress**:
   - Access the dashboard to see learning analytics
   - Review performance trends and recommendations
   - Track improvement over time

#### For Educators/Administrators

1. **Access Analytics**:
   - Navigate to the Analytics page
   - View individual and group performance
   - Analyze learning patterns and trends

2. **Monitor Sessions**:
   - Check the Sessions page for detailed session data
   - Review student engagement and performance metrics
   - Identify areas for intervention

3. **Configure Settings**:
   - Access the Settings page for system configuration
   - Test OpenVINO integration and performance
   - Adjust application parameters

#### API Usage

The application provides RESTful APIs for integration:

```bash
# Get system status
curl http://localhost:5000/api/openvino/status

# Analyze learning style
curl -X POST http://localhost:5000/api/openvino/analyze_learning_style \
  -H "Content-Type: application/json" \
  -d '{"interaction_data": [0.8, 0.6, 0.4, 0.7, 0.5]}'

# Predict performance
curl -X POST http://localhost:5000/api/openvino/predict_performance \
  -H "Content-Type: application/json" \
  -d '{"historical_data": [0.6, 0.7, 0.8, 0.75, 0.85]}'

# Optimize content delivery
curl -X POST http://localhost:5000/api/openvino/optimize_content \
  -H "Content-Type: application/json" \
  -d '{"learning_style": "visual", "current_performance": 0.8}'
```

## Extensibility

### Database Integration

Replace SQLite with a production database:

```python
# In app.py, modify the DATABASE variable
DATABASE = 'postgresql://user:password@localhost/neurolearn'
```

### Custom OpenVINO Models

Extend or replace the default models in `openvino_utils.py`:

```python
# Load your custom model
model = ie.read_model("path/to/your/model.xml")
compiled_model = ie.compile_model(model, "CPU")
```

### Frontend Customization

Modify templates in the `templates/` directory:
- `base.html`: Main layout template
- `dashboard.html`: Dashboard interface
- `analytics.html`: Analytics and charts
- `settings.html`: Configuration interface

### API Extensions

Add new endpoints in `app.py`:

```python
@app.route('/api/custom_endpoint', methods=['GET'])
def custom_endpoint():
    # Your custom logic here
    return jsonify({'success': True})
```

## Replacing Demo Data

### Student Data

Replace demo data with real student records:

```python
# In app.py, modify the student endpoints
@app.route('/api/students')
def get_students():
    # Connect to your real database
    students = db.query("SELECT * FROM students")
    return jsonify(students)
```

### Learning Sessions

Integrate real exercises and user input:

```python
# Replace simulated questions with real content
def generate_real_questions(subject, difficulty):
    # Fetch from your content management system
    return real_questions
```

### Analytics Integration

Connect to your analytics pipeline:

```python
# Replace demo analytics with real data
def get_real_analytics():
    # Connect to your analytics system
    return real_analytics_data
```

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments

- Intel OpenVINO for AI inference capabilities
- Bootstrap for responsive UI framework
- Flask for web application framework
- All contributors and supporters of adaptive learning technology 