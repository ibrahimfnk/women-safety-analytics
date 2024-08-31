# women-safety-analytics

This project is a real-time gender detection system using computer vision techniques. It utilizes YOLOv8 for face detection and an OpenCV-based gender classification model to determine and count male and female individuals from a live video feed.

## Installation

To set up the project on your local machine, follow these steps:

```bash
# Clone the repository
git clone https://github.com/ibrahimfnk/women-safety-analytics.git
cd repository

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

# Install the required packages
pip install -r requirements.txt

# Start the Flask application
cd app/
python app.py