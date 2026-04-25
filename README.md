# 🧴 Skin Analysis AI Web App

An AI-powered web application that analyzes facial skin using image processing and machine learning techniques. The app detects skin conditions, predicts skin type, and provides personalized skincare recommendations.

---

## 🚀 Features

* 📸 Real-time image capture (camera + file upload)
* 🧠 AI-based skin analysis using MobileNetV2
* 🔍 Detects skin conditions:

  * Acne
  * Eczema
  * Psoriasis
  * Hyperpigmentation
  * Wrinkles
  * Eye bags
* 🧴 Personalized skincare recommendations
* 📊 Skin progress tracking
* 👤 User authentication (Signup / Login)
* 📅 Consultation booking system

---

## 🛠️ Tech Stack

* **Backend:** Python, Flask
* **Frontend:** HTML, CSS, JavaScript
* **Database:** SQLite (SQLAlchemy ORM)
* **AI/ML:** TensorFlow, MobileNetV2
* **Image Processing:** OpenCV
* **Authentication:** Werkzeug Security

---

## 📂 Project Structure

```
project/
│── app.py
│── models.py
│── extensions.py
│── static/
│   └── uploads/
│── templates/
│── database.db
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the repository

```
git clone https://github.com/yourusername/skin-analysis-ai.git
cd skin-analysis-ai
```

### 2️⃣ Create virtual environment

```
python -m venv venv
venv\Scripts\activate   (Windows)
```

### 3️⃣ Install dependencies

```
pip install -r requirements.txt
```

### 4️⃣ Run the application

```
python app.py
```

---

## 🌐 Usage

1. Open browser:

   ```
   http://127.0.0.1:5000/
   ```
2. Sign up / Login
3. Upload or capture face image
4. View analysis results and recommendations

---

## 📊 How It Works

* Images are processed using **OpenCV**
* Enhanced with brightness & noise reduction techniques
* Passed to **MobileNetV2 model**
* Generates:

  * Skin type
  * Condition severity
  * Recommendations

---

## ⚠️ Note

* Current model uses **mock scores** for skin conditions
* For production, a **trained dermatology dataset model** is recommended

---

## 🔮 Future Improvements

* Integrate real trained ML model
* Improve accuracy of skin condition detection
* Deploy on cloud (AWS / Render)
* Add dermatologist consultation API
* Mobile app version

---

## 👩‍💻 Author

**Prajakta Kadalagekar**
---

## ⭐ Contribute

Feel free to fork this repo and improve the project!

---

## 📜 License

This project is for educational purposes.
