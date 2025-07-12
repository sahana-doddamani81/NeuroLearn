from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import numpy as np
import json
import os
from datetime import datetime, timedelta
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import random
from collections import defaultdict
import sqlite3
from functools import wraps
import uuid
from openvino.runtime import Core

app = Flask(__name__)
CORS(app)

# Configuration
DATABASE = 'adaptive_learning.db'
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize OpenVINO
ie = Core()

# Enhanced Question Database
QUESTION_BANK = {
            'math': {
            'easy': [
                {'id': 'math_e1', 'question': 'What is 5 + 3?', 'options': ['6', '7', '8', '9'], 'answer': '8', 'concept': 'addition'},
                {'id': 'math_e2', 'question': 'What is 12 - 7?', 'options': ['4', '5', '6', '7'], 'answer': '5', 'concept': 'subtraction'},
                {'id': 'math_e3', 'question': 'What is 4 × 2?', 'options': ['6', '7', '8', '9'], 'answer': '8', 'concept': 'multiplication'},
                {'id': 'math_e4', 'question': 'What is 15 ÷ 3?', 'options': ['3', '4', '5', '6'], 'answer': '5', 'concept': 'division'},
                {'id': 'math_e5', 'question': 'Which is larger: 0.5 or 0.3?', 'options': ['0.5', '0.3', 'Same', 'Cannot tell'], 'answer': '0.5', 'concept': 'decimals'},
                # Visual questions
                {'id': 'math_e6', 'question': 'Look at this pattern: 2, 4, 6, 8, ___. What comes next?', 'options': ['9', '10', '11', '12'], 'answer': '10', 'concept': 'patterns'},
                {'id': 'math_e7', 'question': 'If you draw 3 circles and 2 squares, how many shapes do you have?', 'options': ['4', '5', '6', '7'], 'answer': '5', 'concept': 'counting'},
                # Auditory questions
                {'id': 'math_e8', 'question': 'If someone says "three plus four" out loud, what is the answer?', 'options': ['5', '6', '7', '8'], 'answer': '7', 'concept': 'addition'},
                {'id': 'math_e9', 'question': 'Listen: "Take away two from eight." What number remains?', 'options': ['4', '5', '6', '7'], 'answer': '6', 'concept': 'subtraction'},
                # Kinesthetic questions
                {'id': 'math_e10', 'question': 'If you move 3 steps forward and 1 step back, how many steps are you from where you started?', 'options': ['1', '2', '3', '4'], 'answer': '2', 'concept': 'movement'},
                {'id': 'math_e11', 'question': 'Build a tower with 4 blocks, then add 2 more. How many blocks total?', 'options': ['5', '6', '7', '8'], 'answer': '6', 'concept': 'addition'},
            ],
        'medium': [
            {'id': 'math_m1', 'question': 'What is 15% of 80?', 'options': ['10', '12', '15', '20'], 'answer': '12', 'concept': 'percentages'},
            {'id': 'math_m2', 'question': 'Solve for x: 2x + 5 = 13', 'options': ['3', '4', '5', '6'], 'answer': '4', 'concept': 'algebra'},
            {'id': 'math_m3', 'question': 'What is the area of a rectangle with length 8 and width 5?', 'options': ['13', '26', '40', '80'], 'answer': '40', 'concept': 'geometry'},
            {'id': 'math_m4', 'question': 'What is 2³?', 'options': ['6', '8', '9', '12'], 'answer': '8', 'concept': 'exponents'},
            {'id': 'math_m5', 'question': 'What is the square root of 64?', 'options': ['6', '7', '8', '9'], 'answer': '8', 'concept': 'roots'},
            # Visual questions
            {'id': 'math_m6', 'question': 'Look at this graph: if the line goes up 3 units for every 2 units across, what is the slope?', 'options': ['1.5', '2', '2.5', '3'], 'answer': '1.5', 'concept': 'slope'},
            {'id': 'math_m7', 'question': 'Visualize a circle with radius 3. What is its area?', 'options': ['6π', '9π', '12π', '15π'], 'answer': '9π', 'concept': 'area'},
            # Auditory questions
            {'id': 'math_m8', 'question': 'If someone says "fifteen percent of eighty" aloud, what number do you hear?', 'options': ['10', '12', '15', '20'], 'answer': '12', 'concept': 'percentages'},
            {'id': 'math_m9', 'question': 'Listen: "Two times x plus five equals thirteen." What is x?', 'options': ['3', '4', '5', '6'], 'answer': '4', 'concept': 'algebra'},
            # Kinesthetic questions
            {'id': 'math_m10', 'question': 'If you walk 3 steps north and 4 steps east, how far are you from your starting point?', 'options': ['5 steps', '6 steps', '7 steps', '8 steps'], 'answer': '5 steps', 'concept': 'distance'},
            {'id': 'math_m11', 'question': 'Build a cube with side length 2. What is its volume?', 'options': ['4', '6', '8', '10'], 'answer': '8', 'concept': 'volume'},
        ],
        'hard': [
            {'id': 'math_h1', 'question': 'If f(x) = 2x² + 3x - 1, what is f(3)?', 'options': ['26', '28', '30', '32'], 'answer': '26', 'concept': 'functions'},
            {'id': 'math_h2', 'question': 'What is the derivative of x³ + 2x²?', 'options': ['3x² + 4x', '3x + 4', 'x² + 2x', '3x² + 2x'], 'answer': '3x² + 4x', 'concept': 'calculus'},
            {'id': 'math_h3', 'question': 'In a triangle with sides 3, 4, and 5, what is the largest angle?', 'options': ['30°', '45°', '60°', '90°'], 'answer': '90°', 'concept': 'trigonometry'},
            {'id': 'math_h4', 'question': 'What is log₂(16)?', 'options': ['2', '3', '4', '8'], 'answer': '4', 'concept': 'logarithms'},
            {'id': 'math_h5', 'question': 'What is the sum of the first 10 terms of the sequence 2, 4, 6, 8, ...?', 'options': ['100', '110', '120', '130'], 'answer': '110', 'concept': 'sequences'},
        ]
    },
            'science': {
            'easy': [
                {'id': 'sci_e1', 'question': 'What is the chemical symbol for water?', 'options': ['H2O', 'CO2', 'O2', 'H2'], 'answer': 'H2O', 'concept': 'chemistry'},
                {'id': 'sci_e2', 'question': 'How many planets are in our solar system?', 'options': ['7', '8', '9', '10'], 'answer': '8', 'concept': 'astronomy'},
                {'id': 'sci_e3', 'question': 'What gas do plants absorb from the atmosphere?', 'options': ['Oxygen', 'Nitrogen', 'Carbon Dioxide', 'Hydrogen'], 'answer': 'Carbon Dioxide', 'concept': 'biology'},
                {'id': 'sci_e4', 'question': 'What is the force that pulls objects toward Earth?', 'options': ['Magnetism', 'Gravity', 'Friction', 'Pressure'], 'answer': 'Gravity', 'concept': 'physics'},
                {'id': 'sci_e5', 'question': 'What is the hardest natural substance?', 'options': ['Gold', 'Iron', 'Diamond', 'Quartz'], 'answer': 'Diamond', 'concept': 'materials'},
                # Visual questions
                {'id': 'sci_e6', 'question': 'Look at this diagram of a plant cell. What structure contains the genetic material?', 'options': ['Cell wall', 'Nucleus', 'Chloroplast', 'Mitochondria'], 'answer': 'Nucleus', 'concept': 'cell biology'},
                {'id': 'sci_e7', 'question': 'Visualize the solar system. Which planet is closest to the Sun?', 'options': ['Venus', 'Mercury', 'Earth', 'Mars'], 'answer': 'Mercury', 'concept': 'astronomy'},
                # Auditory questions
                {'id': 'sci_e8', 'question': 'Listen to the sound of thunder. What causes this sound?', 'options': ['Lightning', 'Rain', 'Wind', 'Clouds'], 'answer': 'Lightning', 'concept': 'physics'},
                {'id': 'sci_e9', 'question': 'If you hear a bird singing, what type of communication is this?', 'options': ['Visual', 'Auditory', 'Chemical', 'Tactile'], 'answer': 'Auditory', 'concept': 'biology'},
                # Kinesthetic questions
                {'id': 'sci_e10', 'question': 'If you touch a hot stove and quickly pull your hand away, what type of response is this?', 'options': ['Voluntary', 'Reflex', 'Learned', 'Conditioned'], 'answer': 'Reflex', 'concept': 'biology'},
                {'id': 'sci_e11', 'question': 'When you move your arm, what type of tissue contracts?', 'options': ['Nerve', 'Muscle', 'Bone', 'Cartilage'], 'answer': 'Muscle', 'concept': 'anatomy'},
            ],
        'medium': [
            {'id': 'sci_m1', 'question': 'What is the powerhouse of the cell?', 'options': ['Nucleus', 'Mitochondria', 'Ribosome', 'Cytoplasm'], 'answer': 'Mitochondria', 'concept': 'cell biology'},
            {'id': 'sci_m2', 'question': 'What is the speed of light in vacuum?', 'options': ['3×10⁸ m/s', '3×10⁶ m/s', '3×10⁹ m/s', '3×10⁷ m/s'], 'answer': '3×10⁸ m/s', 'concept': 'physics'},
            {'id': 'sci_m3', 'question': 'Which element has the atomic number 6?', 'options': ['Oxygen', 'Carbon', 'Nitrogen', 'Hydrogen'], 'answer': 'Carbon', 'concept': 'chemistry'},
            {'id': 'sci_m4', 'question': 'What type of rock is formed by cooling magma?', 'options': ['Sedimentary', 'Metamorphic', 'Igneous', 'Crystalline'], 'answer': 'Igneous', 'concept': 'geology'},
            {'id': 'sci_m5', 'question': 'What is the process by which plants make food?', 'options': ['Respiration', 'Photosynthesis', 'Transpiration', 'Digestion'], 'answer': 'Photosynthesis', 'concept': 'biology'},
        ],
        'hard': [
            {'id': 'sci_h1', 'question': 'What is the uncertainty principle in quantum mechanics?', 'options': ['Position and momentum cannot be measured simultaneously with perfect accuracy', 'Energy cannot be created or destroyed', 'Matter and energy are equivalent', 'Time is relative'], 'answer': 'Position and momentum cannot be measured simultaneously with perfect accuracy', 'concept': 'quantum physics'},
            {'id': 'sci_h2', 'question': 'What is the molecular formula of glucose?', 'options': ['C6H12O6', 'C6H6O6', 'C12H22O11', 'C2H6O'], 'answer': 'C6H12O6', 'concept': 'biochemistry'},
            {'id': 'sci_h3', 'question': 'What is the half-life of Carbon-14?', 'options': ['5,730 years', '1,600 years', '24,000 years', '4.5 billion years'], 'answer': '5,730 years', 'concept': 'nuclear physics'},
            {'id': 'sci_h4', 'question': 'Which enzyme breaks down starch into sugars?', 'options': ['Pepsin', 'Amylase', 'Lipase', 'Trypsin'], 'answer': 'Amylase', 'concept': 'biochemistry'},
            {'id': 'sci_h5', 'question': 'What is the name of the boundary around a black hole?', 'options': ['Event Horizon', 'Schwarzschild Radius', 'Photon Sphere', 'Singularity'], 'answer': 'Event Horizon', 'concept': 'astrophysics'},
        ]
    },
            'english': {
            'easy': [
                {'id': 'eng_e1', 'question': 'What is the plural of "child"?', 'options': ['childs', 'children', 'childes', 'child'], 'answer': 'children', 'concept': 'grammar'},
                {'id': 'eng_e2', 'question': 'Which word is a noun?', 'options': ['quickly', 'beautiful', 'happiness', 'run'], 'answer': 'happiness', 'concept': 'parts of speech'},
                {'id': 'eng_e3', 'question': 'What is the opposite of "hot"?', 'options': ['warm', 'cool', 'cold', 'mild'], 'answer': 'cold', 'concept': 'vocabulary'},
                {'id': 'eng_e4', 'question': 'Which sentence is correct?', 'options': ['I am going to the store', 'I is going to the store', 'I are going to the store', 'I be going to the store'], 'answer': 'I am going to the store', 'concept': 'grammar'},
                {'id': 'eng_e5', 'question': 'What is a synonym for "big"?', 'options': ['small', 'large', 'tiny', 'short'], 'answer': 'large', 'concept': 'vocabulary'},
                # Visual questions
                {'id': 'eng_e6', 'question': 'Look at this picture of a cat. What color is it?', 'options': ['Black', 'White', 'Orange', 'Brown'], 'answer': 'Orange', 'concept': 'descriptive language'},
                {'id': 'eng_e7', 'question': 'Visualize a red apple. What color is it?', 'options': ['Green', 'Red', 'Yellow', 'Purple'], 'answer': 'Red', 'concept': 'colors'},
                # Auditory questions
                {'id': 'eng_e8', 'question': 'Listen to the word "beautiful." How many syllables does it have?', 'options': ['2', '3', '4', '5'], 'answer': '3', 'concept': 'phonetics'},
                {'id': 'eng_e9', 'question': 'If someone says "hello" to you, what should you say back?', 'options': ['Goodbye', 'Hello', 'Thank you', 'Please'], 'answer': 'Hello', 'concept': 'conversation'},
                # Kinesthetic questions
                {'id': 'eng_e10', 'question': 'If you move your hand up and down, what action are you performing?', 'options': ['Waving', 'Clapping', 'Pointing', 'Holding'], 'answer': 'Waving', 'concept': 'action words'},
                {'id': 'eng_e11', 'question': 'When you touch something soft, what sense are you using?', 'options': ['Sight', 'Hearing', 'Touch', 'Taste'], 'answer': 'Touch', 'concept': 'senses'},
            ],
        'medium': [
            {'id': 'eng_m1', 'question': 'What is the past tense of "write"?', 'options': ['writed', 'wrote', 'written', 'writes'], 'answer': 'wrote', 'concept': 'verb tenses'},
            {'id': 'eng_m2', 'question': 'Which is an example of alliteration?', 'options': ['The sun is bright', 'Peter picked peppers', 'It was very cold', 'She ran quickly'], 'answer': 'Peter picked peppers', 'concept': 'literary devices'},
            {'id': 'eng_m3', 'question': 'What is the main idea of a paragraph called?', 'options': ['Supporting detail', 'Topic sentence', 'Conclusion', 'Introduction'], 'answer': 'Topic sentence', 'concept': 'reading comprehension'},
            {'id': 'eng_m4', 'question': 'Which word is an adverb?', 'options': ['happy', 'quickly', 'book', 'green'], 'answer': 'quickly', 'concept': 'parts of speech'},
            {'id': 'eng_m5', 'question': 'What punctuation ends a question?', 'options': ['Period', 'Exclamation mark', 'Question mark', 'Comma'], 'answer': 'Question mark', 'concept': 'punctuation'},
        ],
        'hard': [
            {'id': 'eng_h1', 'question': 'What is the literary term for giving human characteristics to non-human things?', 'options': ['Metaphor', 'Simile', 'Personification', 'Hyperbole'], 'answer': 'Personification', 'concept': 'literary devices'},
            {'id': 'eng_h2', 'question': 'In "The road not taken" by Robert Frost, what does the road symbolize?', 'options': ['A journey', 'Life choices', 'Time', 'Nature'], 'answer': 'Life choices', 'concept': 'literary analysis'},
            {'id': 'eng_h3', 'question': 'What is the difference between "affect" and "effect"?', 'options': ['No difference', 'Affect is a verb, effect is a noun', 'Affect is a noun, effect is a verb', 'They are synonyms'], 'answer': 'Affect is a verb, effect is a noun', 'concept': 'grammar'},
            {'id': 'eng_h4', 'question': 'What is iambic pentameter?', 'options': ['A type of rhyme scheme', 'A poetic meter with 10 syllables per line', 'A literary device', 'A type of stanza'], 'answer': 'A poetic meter with 10 syllables per line', 'concept': 'poetry'},
            {'id': 'eng_h5', 'question': 'Which is an example of dramatic irony?', 'options': ['A character says one thing but means another', 'The audience knows something a character doesn\'t', 'A situation turns out opposite to what\'s expected', 'A character is contradictory'], 'answer': 'The audience knows something a character doesn\'t', 'concept': 'literary devices'},
        ]
    }
}

# Enhanced Student Profiles
STUDENT_PROFILES = [
    {
        'id': 'student_1',
        'name': 'Emma Johnson',
        'age': 14,
        'grade': 8,
        'learning_preferences': ['visual', 'kinesthetic'],
        'subjects': ['math', 'science'],
        'performance_history': [],
        'learning_disabilities': [],
        'interests': ['art', 'nature', 'puzzles'],
        'created_at': datetime.now().isoformat()
    },
    {
        'id': 'student_2',
        'name': 'Alex Chen',
        'age': 16,
        'grade': 10,
        'learning_preferences': ['auditory', 'visual'],
        'subjects': ['math', 'science', 'english'],
        'performance_history': [],
        'learning_disabilities': ['dyslexia'],
        'interests': ['music', 'technology', 'reading'],
        'created_at': datetime.now().isoformat()
    },
    {
        'id': 'student_3',
        'name': 'Maya Patel',
        'age': 12,
        'grade': 6,
        'learning_preferences': ['kinesthetic', 'social'],
        'subjects': ['english', 'science'],
        'performance_history': [],
        'learning_disabilities': [],
        'interests': ['sports', 'group activities', 'animals'],
        'created_at': datetime.now().isoformat()
    },
    {
        'id': 'student_4',
        'name': 'Jordan Williams',
        'age': 15,
        'grade': 9,
        'learning_preferences': ['visual', 'logical'],
        'subjects': ['math', 'science'],
        'performance_history': [],
        'learning_disabilities': ['ADHD'],
        'interests': ['games', 'coding', 'mathematics'],
        'created_at': datetime.now().isoformat()
    }
]

class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Students table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER,
                grade INTEGER,
                learning_preferences TEXT,
                subjects TEXT,
                learning_disabilities TEXT,
                interests TEXT,
                created_at TEXT
            )
        ''')
        
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                student_id TEXT,
                subject TEXT,
                difficulty TEXT,
                questions_asked INTEGER,
                correct_answers INTEGER,
                total_time REAL,
                engagement_score REAL,
                created_at TEXT,
                FOREIGN KEY (student_id) REFERENCES students (id)
            )
        ''')
        
        # Question responses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS question_responses (
                id TEXT PRIMARY KEY,
                session_id TEXT,
                question_id TEXT,
                selected_answer TEXT,
                correct_answer TEXT,
                is_correct BOOLEAN,
                time_taken REAL,
                created_at TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions (id)
            )
        ''')
        
        # Learning analytics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_analytics (
                id TEXT PRIMARY KEY,
                student_id TEXT,
                learning_style_visual REAL,
                learning_style_auditory REAL,
                learning_style_kinesthetic REAL,
                performance_prediction REAL,
                recommended_difficulty TEXT,
                created_at TEXT,
                FOREIGN KEY (student_id) REFERENCES students (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Insert sample students if table is empty
        self.insert_sample_data()

    def insert_sample_data(self):
        """Insert sample students if database is empty"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM students')
        count = cursor.fetchone()[0]
        
        # Only insert sample data if database is completely empty
        # This ensures real student data takes priority
        if count == 0:
            print("Database is empty. Inserting minimal sample data for demonstration...")
            for student in STUDENT_PROFILES:
                cursor.execute('''
                    INSERT INTO students (id, name, age, grade, learning_preferences, 
                                        subjects, learning_disabilities, interests, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    student['id'],
                    student['name'],
                    student['age'],
                    student['grade'],
                    json.dumps(student['learning_preferences']),
                    json.dumps(student['subjects']),
                    json.dumps(student['learning_disabilities']),
                    json.dumps(student['interests']),
                    student['created_at']
                ))
            
            # Insert minimal sample sessions for demonstration
            self.insert_sample_sessions()
        else:
            print(f"Database contains {count} students. Real student data will be prioritized.")
        
        conn.commit()
        conn.close()

    def insert_sample_sessions(self):
        """Insert sample sessions for realistic data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Sample sessions for each student
        sample_sessions = [
            {
                'student_id': 'student_1',
                'subject': 'math',
                'difficulty': 'medium',
                'questions_asked': 10,
                'correct_answers': 8,
                'total_time': 450,
                'engagement_score': 0.85
            },
            {
                'student_id': 'student_1',
                'subject': 'science',
                'difficulty': 'easy',
                'questions_asked': 8,
                'correct_answers': 7,
                'total_time': 320,
                'engagement_score': 0.78
            },
            {
                'student_id': 'student_2',
                'subject': 'math',
                'difficulty': 'hard',
                'questions_asked': 12,
                'correct_answers': 9,
                'total_time': 600,
                'engagement_score': 0.92
            },
            {
                'student_id': 'student_2',
                'subject': 'english',
                'difficulty': 'medium',
                'questions_asked': 10,
                'correct_answers': 8,
                'total_time': 380,
                'engagement_score': 0.88
            },
            {
                'student_id': 'student_3',
                'subject': 'science',
                'difficulty': 'easy',
                'questions_asked': 8,
                'correct_answers': 6,
                'total_time': 280,
                'engagement_score': 0.75
            },
            {
                'student_id': 'student_4',
                'subject': 'math',
                'difficulty': 'medium',
                'questions_asked': 10,
                'correct_answers': 7,
                'total_time': 420,
                'engagement_score': 0.82
            }
        ]
        
        for session in sample_sessions:
            session_id = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO sessions (id, student_id, subject, difficulty, questions_asked,
                                    correct_answers, total_time, engagement_score, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session_id,
                session['student_id'],
                session['subject'],
                session['difficulty'],
                session['questions_asked'],
                session['correct_answers'],
                session['total_time'],
                session['engagement_score'],
                (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
            ))
        
        conn.commit()
        conn.close()

    def get_all_students(self):
        """Get all students from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM students')
        rows = cursor.fetchall()
        
        students = []
        for row in rows:
            student = {
                'id': row[0],
                'name': row[1],
                'age': row[2],
                'grade': row[3],
                'learning_preferences': json.loads(row[4]),
                'subjects': json.loads(row[5]),
                'learning_disabilities': json.loads(row[6]),
                'interests': json.loads(row[7]),
                'created_at': row[8]
            }
            students.append(student)
        
        conn.close()
        return students

    def get_student_by_id(self, student_id):
        """Get a specific student by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM students WHERE id = ?', (student_id,))
        row = cursor.fetchone()
        
        if row:
            student = {
                'id': row[0],
                'name': row[1],
                'age': row[2],
                'grade': row[3],
                'learning_preferences': json.loads(row[4]),
                'subjects': json.loads(row[5]),
                'learning_disabilities': json.loads(row[6]),
                'interests': json.loads(row[7]),
                'created_at': row[8]
            }
            conn.close()
            return student
        
        conn.close()
        return None

    def save_session(self, session_data):
        """Save a learning session to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        session_id = str(uuid.uuid4())
        cursor.execute('''
            INSERT INTO sessions (id, student_id, subject, difficulty, questions_asked,
                                correct_answers, total_time, engagement_score, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id,
            session_data['student_id'],
            session_data['subject'],
            session_data['difficulty'],
            session_data['questions_asked'],
            session_data['correct_answers'],
            session_data['total_time'],
            session_data['engagement_score'],
            datetime.now().isoformat()
        ))
        
        # Save individual question responses
        for response in session_data['responses']:
            response_id = str(uuid.uuid4())
            
            # Map frontend fields to backend expected fields
            question_id = response.get('question_id', f'q_{response_id[:8]}')  # Generate if not provided
            selected_answer = response.get('selected_answer', response.get('selected', ''))
            correct_answer = response.get('correct_answer', '')  # Will be set based on is_correct
            is_correct = response.get('is_correct', False)
            time_taken = response.get('time_taken', 0)
            
            # If we have the question text, extract the correct answer
            if 'question' in response and 'options' in response:
                question_text = response['question']
                options = response.get('options', [])
                correct_index = response.get('correct', 0)
                if correct_index < len(options):
                    correct_answer = options[correct_index]
            
            cursor.execute('''
                INSERT INTO question_responses (id, session_id, question_id, selected_answer,
                                              correct_answer, is_correct, time_taken, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                response_id,
                session_id,
                question_id,
                selected_answer,
                correct_answer,
                is_correct,
                time_taken,
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
        return session_id

    def get_student_sessions(self, student_id):
        """Get all sessions for a student"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT s.*, GROUP_CONCAT(qr.question_id) as questions
            FROM sessions s
            LEFT JOIN question_responses qr ON s.id = qr.session_id
            WHERE s.student_id = ?
            GROUP BY s.id
            ORDER BY s.created_at DESC
        ''', (student_id,))
        
        sessions = []
        for row in cursor.fetchall():
            session = {
                'id': row[0],
                'student_id': row[1],
                'subject': row[2],
                'difficulty': row[3],
                'questions_asked': row[4],
                'correct_answers': row[5],
                'total_time': row[6],
                'engagement_score': row[7],
                'created_at': row[8],
                'questions': row[9].split(',') if row[9] else []
            }
            sessions.append(session)
        
        conn.close()
        return sessions

# Initialize database
db_manager = DatabaseManager(DATABASE)
# Only insert sample data if explicitly needed for demonstration
# db_manager.insert_sample_data()  # Uncomment only for initial demo setup

class AdaptiveLearningEngine:
    def __init__(self):
        self.learning_styles = ['visual', 'auditory', 'kinesthetic', 'reading']
        self.difficulty_levels = ['easy', 'medium', 'hard']
        self.performance_threshold = {'easy': 0.8, 'medium': 0.7, 'hard': 0.6}
        
        # Initialize OpenVINO analyzer
        try:
            from openvino_utils import OpenVINOLearningAnalyzer
            self.openvino_analyzer = OpenVINOLearningAnalyzer()
            self.openvino_analyzer.initialize_models()
            self.openvino_available = True
        except Exception as e:
            print(f"OpenVINO not available: {e}")
            self.openvino_available = False

    def analyze_learning_style(self, student_id, session_data):
        """Analyze learning style based on performance patterns using OpenVINO insights"""
        sessions = db_manager.get_student_sessions(student_id)
        
        if len(sessions) < 2:
            return {
                'visual': 0.33,
                'auditory': 0.33,
                'kinesthetic': 0.33,
                'dominant': 'visual',
                'confidence': 0.1
            }
        
        # Use OpenVINO for pattern analysis
        try:
            # Prepare data for OpenVINO analysis
            interaction_data = []
            for session in sessions:
                accuracy = session['correct_answers'] / session['questions_asked'] if session['questions_asked'] > 0 else 0
                avg_time = session['total_time'] / session['questions_asked'] if session['questions_asked'] > 0 else 0
                engagement = session.get('engagement_score', 0.5)
                
                # Normalize time (0-1 scale)
                normalized_time = min(avg_time / 60.0, 1.0)  # Assume 60 seconds is max
                
                interaction_data.extend([accuracy, normalized_time, engagement])
            
            # Use OpenVINO analyzer if available
            if self.openvino_available:
                analysis = self.openvino_analyzer.analyze_learning_patterns(interaction_data)
                return analysis
            else:
                # Fallback to simulated OpenVINO analysis
                return self._simulate_openvino_analysis(interaction_data)
            
        except Exception as e:
            print(f"OpenVINO analysis error: {e}")
            # Fallback to simple analysis
            return self._fallback_analysis(sessions)

    def _simulate_openvino_analysis(self, interaction_data):
        """Simulate OpenVINO analysis when OpenVINO is not available"""
        data = np.array(interaction_data)
        
        # Pad or truncate to 10 features
        if len(data) < 10:
            data = np.pad(data, (0, 10 - len(data)), 'constant', constant_values=0.5)
        elif len(data) > 10:
            data = data[:10]
        
        # Apply PCA for feature reduction (simulating OpenVINO inference)
        from sklearn.preprocessing import StandardScaler
        from sklearn.decomposition import PCA
        
        scaler = StandardScaler()
        pca = PCA(n_components=3)
        
        data_normalized = scaler.fit_transform(data.reshape(1, -1))
        features = pca.fit_transform(data_normalized)
        
        # Simulate neural network inference
        weights = np.random.randn(3, 3) * 0.1
        bias = np.random.randn(3) * 0.1
        
        output = np.tanh(np.dot(features, weights.T) + bias)
        
        # Apply softmax to get probabilities
        exp_output = np.exp(output)
        probabilities = exp_output / np.sum(exp_output)
        
        # Extract learning style scores
        visual_score = float(probabilities[0, 0])
        auditory_score = float(probabilities[0, 1])
        kinesthetic_score = float(probabilities[0, 2])
        
        # Determine dominant learning style
        scores = [visual_score, auditory_score, kinesthetic_score]
        styles = ['visual', 'auditory', 'kinesthetic']
        dominant_style = styles[np.argmax(scores)]
        
        return {
            'visual': visual_score,
            'auditory': auditory_score,
            'kinesthetic': kinesthetic_score,
            'dominant': dominant_style,
            'confidence': float(np.max(scores)),
            'openvino_processed': False  # Simulated
        }

    def _fallback_analysis(self, sessions):
        """Fallback analysis when OpenVINO is not available"""
        visual_score = 0
        auditory_score = 0
        kinesthetic_score = 0
        
        for session in sessions:
            accuracy = session['correct_answers'] / session['questions_asked'] if session['questions_asked'] > 0 else 0
            avg_time = session['total_time'] / session['questions_asked'] if session['questions_asked'] > 0 else 0
            
            # Visual learners tend to be fast and accurate
            if accuracy > 0.7 and avg_time < 20:
                visual_score += 1
            
            # Auditory learners tend to be moderate pace with good retention
            if accuracy > 0.6 and 15 < avg_time < 30:
                auditory_score += 1
            
            # Kinesthetic learners might be slower but thorough
            if avg_time > 25:
                kinesthetic_score += 1
        
        total_sessions = len(sessions)
        visual_pct = visual_score / total_sessions
        auditory_pct = auditory_score / total_sessions
        kinesthetic_pct = kinesthetic_score / total_sessions
        
        # Normalize scores
        total_score = visual_pct + auditory_pct + kinesthetic_pct
        if total_score > 0:
            visual_pct /= total_score
            auditory_pct /= total_score
            kinesthetic_pct /= total_score
        else:
            visual_pct = auditory_pct = kinesthetic_pct = 0.33
        
        # Determine dominant style
        scores = {'visual': visual_pct, 'auditory': auditory_pct, 'kinesthetic': kinesthetic_pct}
        dominant = max(scores, key=scores.get)
        
        confidence = max(scores.values()) - min(scores.values())
        
        return {
            'visual': visual_pct,
            'auditory': auditory_pct,
            'kinesthetic': kinesthetic_pct,
            'dominant': dominant,
            'confidence': confidence,
            'openvino_processed': False
        }

    def predict_performance(self, student_id, subject, difficulty):
        """Predict student performance for given subject and difficulty using OpenVINO"""
        sessions = db_manager.get_student_sessions(student_id)
        
        if not sessions:
            return 0.5  # Default prediction
        
        # Filter sessions by subject and difficulty
        relevant_sessions = [s for s in sessions if s['subject'] == subject and s['difficulty'] == difficulty]
        
        if not relevant_sessions:
            # Use all sessions for the subject
            relevant_sessions = [s for s in sessions if s['subject'] == subject]
        
        if not relevant_sessions:
            return 0.5
        
        # Prepare historical data for OpenVINO prediction
        historical_data = []
        for session in relevant_sessions:
            accuracy = session['correct_answers'] / session['questions_asked'] if session['questions_asked'] > 0 else 0
            historical_data.append(accuracy)
        
        # Use OpenVINO analyzer if available
        if self.openvino_available and len(historical_data) > 0:
            try:
                prediction_result = self.openvino_analyzer.predict_performance(historical_data)
                return prediction_result['predicted_performance']
            except Exception as e:
                print(f"OpenVINO prediction error: {e}")
        
        # Fallback to traditional prediction
        total_accuracy = sum(historical_data)
        predicted_performance = total_accuracy / len(historical_data)
        
        # Apply trend analysis (recent sessions weighted more)
        if len(historical_data) > 1:
            recent_sessions = historical_data[:3]  # Most recent 3 sessions
            recent_avg = sum(recent_sessions) / len(recent_sessions)
            
            # Weighted average (70% recent, 30% historical)
            predicted_performance = 0.7 * recent_avg + 0.3 * predicted_performance
        
        return min(max(predicted_performance, 0.0), 1.0)

    def recommend_difficulty(self, student_id, subject):
        """Recommend appropriate difficulty level"""
        easy_pred = self.predict_performance(student_id, subject, 'easy')
        medium_pred = self.predict_performance(student_id, subject, 'medium')
        hard_pred = self.predict_performance(student_id, subject, 'hard')
        
        # Recommend based on performance thresholds
        if easy_pred < self.performance_threshold['easy']:
            return 'easy'
        elif medium_pred < self.performance_threshold['medium']:
            return 'medium'
        else:
            return 'hard'

    def optimize_content_delivery(self, student_id, learning_style, current_performance):
        """Optimize content delivery using OpenVINO insights"""
        if self.openvino_available:
            try:
                # Get session data for additional context
                sessions = db_manager.get_student_sessions(student_id)
                session_time = 0.5  # Default
                engagement = 0.7    # Default
                
                if sessions:
                    # Calculate average session time and engagement
                    total_time = sum(s.get('total_time', 0) for s in sessions)
                    total_sessions = len(sessions)
                    if total_sessions > 0:
                        session_time = min(total_time / (total_sessions * 60), 1.0)  # Normalize to 0-1
                    
                    # Calculate engagement based on accuracy and time
                    avg_accuracy = sum(s['correct_answers'] / s['questions_asked'] for s in sessions if s['questions_asked'] > 0)
                    if len(sessions) > 0:
                        engagement = avg_accuracy / len(sessions)
                
                optimization = self.openvino_analyzer.optimize_content_delivery(
                    learning_style, current_performance, session_time, engagement
                )
                return optimization
            except Exception as e:
                print(f"OpenVINO optimization error: {e}")
        
        # Fallback to rule-based optimization
        strategies = {
            'visual': {
                'content_type': 'interactive_diagrams',
                'difficulty_adjustment': 0.1 if current_performance > 0.7 else -0.1,
                'engagement_boost': 0.2
            },
            'auditory': {
                'content_type': 'audio_narration',
                'difficulty_adjustment': 0.05 if current_performance > 0.7 else -0.05,
                'engagement_boost': 0.15
            },
            'kinesthetic': {
                'content_type': 'hands_on_activities',
                'difficulty_adjustment': 0.15 if current_performance > 0.7 else -0.15,
                'engagement_boost': 0.25
            }
        }
        
        strategy = strategies.get(learning_style, strategies['visual'])
        
        return {
            'recommended_content_type': strategy['content_type'],
            'difficulty_adjustment': strategy['difficulty_adjustment'],
            'expected_engagement_boost': strategy['engagement_boost'],
            'openvino_processed': False
        }

    def generate_personalized_content(self, student_id, subject, num_questions=5):
        """Generate personalized questions based on student's learning profile"""
        student = db_manager.get_student_by_id(student_id)
        if not student:
            return []
        
        # Get student's learning preferences
        learning_preferences = student.get('learning_preferences', ['visual'])
        primary_style = learning_preferences[0] if learning_preferences else 'visual'
        
        # Determine difficulty
        difficulty = self.recommend_difficulty(student_id, subject)
        
        # Get current performance for optimization
        current_performance = self.predict_performance(student_id, subject, difficulty)
        
        # Optimize content delivery
        optimization = self.optimize_content_delivery(student_id, primary_style, current_performance)
        
        # Get questions for the subject and difficulty
        if subject in QUESTION_BANK and difficulty in QUESTION_BANK[subject]:
            questions = QUESTION_BANK[subject][difficulty].copy()
            
            # Personalize questions based on learning style and optimization
            personalized_questions = self._personalize_questions_for_style(questions, primary_style, num_questions)
            
            # Apply difficulty adjustment from OpenVINO optimization
            if optimization.get('difficulty_adjustment', 0) != 0:
                # Adjust question selection based on difficulty recommendation
                pass  # Implementation would adjust question selection
            
            # Convert to frontend format
            formatted_questions = []
            for q in personalized_questions:
                # Find the index of the correct answer
                correct_index = q['options'].index(q['answer'])
                formatted_questions.append({
                    'question': q['question'],
                    'options': q['options'],
                    'correct': correct_index,
                    'content_type': optimization.get('recommended_content_type', 'standard')
                })
            
            return formatted_questions
        
        return []
    
    def _personalize_questions_for_style(self, questions, learning_style, num_questions):
        """Personalize questions based on learning style"""
        # Create learning-style-specific question sets
        style_specific_questions = {
            'visual': [
                # Visual Math Questions
                {'question': 'Look at this pattern: 2, 4, 6, 8, ___. What comes next?', 'options': ['9', '10', '11', '12'], 'answer': '10'},
                {'question': 'If you draw 3 circles and 2 squares, how many shapes do you have?', 'options': ['4', '5', '6', '7'], 'answer': '5'},
                {'question': 'Visualize a rectangle with length 4 and width 3. What is its area?', 'options': ['7', '12', '14', '16'], 'answer': '12'},
                {'question': 'Look at this graph: if the line goes up 2 units for every 1 unit across, what is the slope?', 'options': ['1', '2', '3', '4'], 'answer': '2'},
                {'question': 'Visualize a circle with radius 2. What is its area?', 'options': ['4π', '8π', '12π', '16π'], 'answer': '4π'},
                
                # Visual Science Questions
                {'question': 'Look at this diagram of a plant cell. What structure contains the genetic material?', 'options': ['Cell wall', 'Nucleus', 'Chloroplast', 'Mitochondria'], 'answer': 'Nucleus'},
                {'question': 'Visualize the solar system. Which planet is closest to the Sun?', 'options': ['Venus', 'Mercury', 'Earth', 'Mars'], 'answer': 'Mercury'},
                {'question': 'Look at this food chain: Grass → Rabbit → Fox. What type of consumer is the fox?', 'options': ['Primary', 'Secondary', 'Tertiary', 'Producer'], 'answer': 'Secondary'},
                {'question': 'Visualize a water molecule. How many hydrogen atoms does it have?', 'options': ['1', '2', '3', '4'], 'answer': '2'},
                {'question': 'Look at this diagram of the heart. Which chamber receives oxygenated blood?', 'options': ['Left atrium', 'Right atrium', 'Left ventricle', 'Right ventricle'], 'answer': 'Left atrium'},
                
                # Visual English Questions
                {'question': 'Look at this picture of a cat. What color is it?', 'options': ['Black', 'White', 'Orange', 'Brown'], 'answer': 'Orange'},
                {'question': 'Visualize a red apple. What color is it?', 'options': ['Green', 'Red', 'Yellow', 'Purple'], 'answer': 'Red'},
                {'question': 'Look at this sentence: "The quick brown fox jumps over the lazy dog." How many words are in this sentence?', 'options': ['8', '9', '10', '11'], 'answer': '9'},
                {'question': 'Visualize the word "beautiful." How many letters does it have?', 'options': ['7', '8', '9', '10'], 'answer': '9'},
                {'question': 'Look at this pattern: A, B, C, D, ___. What comes next?', 'options': ['E', 'F', 'G', 'H'], 'answer': 'E'}
            ],
            'auditory': [
                # Auditory Language Questions
                {'question': 'Listen to the word "beautiful." How many syllables does it have?', 'options': ['2', '3', '4', '5'], 'answer': '3'},
                {'question': 'If someone says "hello" to you, what should you say back?', 'options': ['Goodbye', 'Hello', 'Thank you', 'Please'], 'answer': 'Hello'},
                {'question': 'Listen to this sentence: "The cat sat on the mat." What is the subject?', 'options': ['The', 'Cat', 'Sat', 'Mat'], 'answer': 'Cat'},
                {'question': 'If someone asks "How are you?" what is the most common response?', 'options': ['Goodbye', 'I am fine', 'Thank you', 'Please'], 'answer': 'I am fine'},
                {'question': 'Listen to the word "pronunciation." How many syllables does it have?', 'options': ['3', '4', '5', '6'], 'answer': '5'},
                
                # Auditory Communication Questions
                {'question': 'If you hear a bird singing, what type of communication is this?', 'options': ['Visual', 'Auditory', 'Chemical', 'Tactile'], 'answer': 'Auditory'},
                {'question': 'Listen to the sound of thunder. What causes this sound?', 'options': ['Lightning', 'Rain', 'Wind', 'Clouds'], 'answer': 'Lightning'},
                {'question': 'If someone speaks in a whisper, what does this usually indicate?', 'options': ['Anger', 'Secrecy', 'Excitement', 'Boredom'], 'answer': 'Secrecy'},
                {'question': 'Listen to this rhythm: da-da-DUM, da-da-DUM. What type of pattern is this?', 'options': ['Visual', 'Auditory', 'Kinesthetic', 'Temporal'], 'answer': 'Auditory'},
                {'question': 'If you hear someone say "excuse me," what are they usually doing?', 'options': ['Greeting', 'Apologizing', 'Asking a question', 'Giving directions'], 'answer': 'Apologizing'},
                
                # Auditory Music Questions
                {'question': 'Listen to a high-pitched sound. What characteristic is this describing?', 'options': ['Volume', 'Pitch', 'Tone', 'Rhythm'], 'answer': 'Pitch'},
                {'question': 'If you hear a drum beat, what type of instrument is this?', 'options': ['String', 'Wind', 'Percussion', 'Brass'], 'answer': 'Percussion'},
                {'question': 'Listen to someone speaking quickly. What does this usually indicate?', 'options': ['Nervousness', 'Calmness', 'Boredom', 'Confidence'], 'answer': 'Nervousness'},
                {'question': 'If you hear a loud noise, what sense are you using?', 'options': ['Sight', 'Hearing', 'Touch', 'Smell'], 'answer': 'Hearing'},
                {'question': 'Listen to this word: "pronunciation." Which syllable is stressed?', 'options': ['First', 'Second', 'Third', 'Fourth'], 'answer': 'Fourth'}
            ],
            'kinesthetic': [
                # Kinesthetic Movement Questions
                {'question': 'If you move 3 steps forward and 1 step back, how many steps are you from where you started?', 'options': ['1', '2', '3', '4'], 'answer': '2'},
                {'question': 'If you walk 3 steps north and 4 steps east, how far are you from your starting point?', 'options': ['5 steps', '6 steps', '7 steps', '8 steps'], 'answer': '5 steps'},
                {'question': 'If you move your hand up and down, what action are you performing?', 'options': ['Waving', 'Clapping', 'Pointing', 'Holding'], 'answer': 'Waving'},
                {'question': 'If you touch something soft, what sense are you using?', 'options': ['Sight', 'Hearing', 'Touch', 'Taste'], 'answer': 'Touch'},
                {'question': 'When you move your arm, what type of tissue contracts?', 'options': ['Nerve', 'Muscle', 'Bone', 'Cartilage'], 'answer': 'Muscle'},
                
                # Kinesthetic Building Questions
                {'question': 'Build a tower with 4 blocks, then add 2 more. How many blocks total?', 'options': ['5', '6', '7', '8'], 'answer': '6'},
                {'question': 'If you build a cube with side length 2, what is its volume?', 'options': ['4', '6', '8', '10'], 'answer': '8'},
                {'question': 'If you construct a rectangle with length 5 and width 3, what is its perimeter?', 'options': ['8', '15', '16', '20'], 'answer': '16'},
                {'question': 'If you create a triangle with sides 3, 4, and 5, what type of triangle is it?', 'options': ['Equilateral', 'Isosceles', 'Right', 'Obtuse'], 'answer': 'Right'},
                {'question': 'If you manipulate 6 objects into 2 equal groups, how many are in each group?', 'options': ['2', '3', '4', '5'], 'answer': '3'},
                
                # Kinesthetic Physical Questions
                {'question': 'If you touch a hot stove and quickly pull your hand away, what type of response is this?', 'options': ['Voluntary', 'Reflex', 'Learned', 'Conditioned'], 'answer': 'Reflex'},
                {'question': 'When you lift a heavy object, what type of muscle contraction occurs?', 'options': ['Isometric', 'Isotonic', 'Isokinetic', 'Eccentric'], 'answer': 'Isotonic'},
                {'question': 'If you hold an object in your hand, what type of grip are you using?', 'options': ['Precision', 'Power', 'Hook', 'Lateral'], 'answer': 'Power'},
                {'question': 'When you jump up and down, what type of movement is this?', 'options': ['Linear', 'Rotational', 'Oscillatory', 'Reciprocal'], 'answer': 'Oscillatory'},
                {'question': 'If you balance on one foot, what system helps you maintain balance?', 'options': ['Nervous', 'Muscular', 'Skeletal', 'Vestibular'], 'answer': 'Vestibular'}
            ]
        }
        
        # Get questions for the student's primary learning style
        primary_questions = style_specific_questions.get(learning_style, [])
        
        # If we don't have enough questions for the primary style, supplement with original questions
        if len(primary_questions) < num_questions:
            # Add some original questions to supplement
            all_questions = primary_questions + questions
            random.shuffle(all_questions)
            return all_questions[:num_questions]
        else:
            # We have enough questions for the primary style
            random.shuffle(primary_questions)
            return primary_questions[:num_questions]

    def generate_progress_visualization(self, student_id):
        """Generate comprehensive progress visualization"""
        sessions = db_manager.get_student_sessions(student_id)
        
        if not sessions:
            return None
        
        # Prepare data for visualization
        dates = [datetime.fromisoformat(s['created_at']).date() for s in sessions]
        accuracies = [s['correct_answers'] / s['questions_asked'] if s['questions_asked'] > 0 else 0 for s in sessions]
        subjects = [s['subject'] for s in sessions]
        difficulties = [s['difficulty'] for s in sessions]
        
        # Create multi-panel visualization
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Performance over time
        axes[0, 0].plot(dates, accuracies, marker='o', linewidth=2, markersize=6)
        axes[0, 0].set_title('Performance Over Time', fontsize=14, fontweight='bold')
        axes[0, 0].set_ylabel('Accuracy')
        axes[0, 0].grid(True, alpha=0.3)
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # 2. Performance by subject
        subject_performance = defaultdict(list)
        for session in sessions:
            accuracy = session['correct_answers'] / session['questions_asked'] if session['questions_asked'] > 0 else 0
            subject_performance[session['subject']].append(accuracy)
        
        subject_avg = {subject: np.mean(scores) for subject, scores in subject_performance.items()}
        axes[0, 1].bar(subject_avg.keys(), subject_avg.values(), color=['skyblue', 'lightgreen', 'lightcoral'])
        axes[0, 1].set_title('Average Performance by Subject', fontsize=14, fontweight='bold')
        axes[0, 1].set_ylabel('Average Accuracy')
        axes[0, 1].set_ylim(0, 1)
        
        # 3. Performance by difficulty
        difficulty_performance = defaultdict(list)
        for session in sessions:
            accuracy = session['correct_answers'] / session['questions_asked'] if session['questions_asked'] > 0 else 0
            difficulty_performance[session['difficulty']].append(accuracy)
        
        difficulty_avg = {diff: np.mean(scores) for diff, scores in difficulty_performance.items()}
        if difficulty_avg:
            axes[1, 0].bar(difficulty_avg.keys(), difficulty_avg.values(), color=['lightblue', 'orange', 'red'])
            axes[1, 0].set_title('Performance by Difficulty Level', fontsize=14, fontweight='bold')
            axes[1, 0].set_ylabel('Average Accuracy')
            axes[1, 0].set_ylim(0, 1)
        
        # 4. Learning style analysis
        learning_analysis = self.analyze_learning_style(student_id, {})
        styles = ['Visual', 'Auditory', 'Kinesthetic']
        scores = [learning_analysis['visual'], learning_analysis['auditory'], learning_analysis['kinesthetic']]
        
        axes[1, 1].pie(scores, labels=styles, autopct='%1.1f%%', startangle=90)
        axes[1, 1].set_title('Learning Style Distribution', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        # Convert plot to base64 string
        img = io.BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight', dpi=300)
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()
        plt.close()
        
        return plot_url

# Initialize the adaptive learning engine
learning_engine = AdaptiveLearningEngine()

# API Routes
@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/students')
def students():
    return render_template('students.html')

@app.route('/analytics')
def analytics():
    return render_template('analytics.html')

@app.route('/sessions')
def sessions():
    return render_template('sessions.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/api/students')
def get_students():
    """Get all students with session data"""
    students = db_manager.get_all_students()
    
    # Enhance student data with session information
    enhanced_students = []
    for student in students:
        sessions = db_manager.get_student_sessions(student['id'])
        
        # Calculate student metrics
        total_sessions = len(sessions)
        if sessions:
            recent_accuracy = sessions[0]['correct_answers'] / sessions[0]['questions_asked'] if sessions[0]['questions_asked'] > 0 else 0
            # Get the most recent session date
            last_session_date = sessions[0]['created_at']
        else:
            recent_accuracy = 0
            last_session_date = None
        
        enhanced_student = {
            **student,  # Include all original student data
            'total_sessions': total_sessions,
            'recent_accuracy': recent_accuracy,
            'last_session_date': last_session_date,
            'total_questions_answered': sum(s['questions_asked'] for s in sessions) if sessions else 0
        }
        
        enhanced_students.append(enhanced_student)
    
    return jsonify({'students': enhanced_students})

@app.route('/api/student/<student_id>')
def get_student(student_id):
    """Get a specific student"""
    student = db_manager.get_student_by_id(student_id)
    if student:
        return jsonify({'student': student})
    else:
        return jsonify({'error': 'Student not found'}), 404

@app.route('/api/start_session', methods=['POST'])
def start_session():
    """Start a learning session"""
    data = request.json
    student_id = data.get('student_id')
    subject = data.get('subject', 'math')
    difficulty = data.get('difficulty', 'medium')
    
    # Generate personalized questions
    questions = learning_engine.generate_personalized_content(student_id, subject, 5)
    
    if not questions:
        # Fallback to random questions
        if subject in QUESTION_BANK and difficulty in QUESTION_BANK[subject]:
            raw_questions = random.sample(QUESTION_BANK[subject][difficulty], min(5, len(QUESTION_BANK[subject][difficulty])))
            
            # Convert to frontend format
            questions = []
            for q in raw_questions:
                # Find the index of the correct answer
                correct_index = q['options'].index(q['answer'])
                questions.append({
                    'question': q['question'],
                    'options': q['options'],
                    'correct': correct_index
                })
    
    return jsonify({
        'questions': questions,
        'subject': subject,
        'difficulty': difficulty,
        'message': 'Session started successfully'
    })

@app.route('/api/submit_session', methods=['POST'])
def submit_session():
    """Submit session results and get analysis"""
    data = request.json
    student_id = data.get('student_id')
    subject = data.get('subject')
    difficulty = data.get('difficulty')
    answers = data.get('answers', [])
    
    # Calculate session metrics
    correct_count = sum(1 for answer in answers if answer.get('is_correct', False))
    total_questions = len(answers)
    total_time = sum(answer.get('time_taken', 0) for answer in answers)
    avg_engagement = sum(answer.get('engagement', 0.5) for answer in answers) / total_questions if total_questions > 0 else 0.5
    
    # Save session to database
    session_data = {
        'student_id': student_id,
        'subject': subject,
        'difficulty': difficulty,
        'questions_asked': total_questions,
        'correct_answers': correct_count,
        'total_time': total_time,
        'engagement_score': avg_engagement,
        'responses': answers
    }
    
    session_id = db_manager.save_session(session_data)
    
    # Analyze learning style
    learning_analysis = learning_engine.analyze_learning_style(student_id, session_data)
    
    # Generate recommendations
    recommendations = []
    accuracy = correct_count / total_questions if total_questions > 0 else 0
    
    if accuracy < 0.5:
        recommendations.append("Consider reviewing basic concepts in this subject")
        recommendations.append("Take more time to read questions carefully")
    if accuracy > 0.8:
        recommendations.append("Excellent performance! Consider more challenging content")
    if total_time / total_questions < 10:
        recommendations.append("Try to think through problems more thoroughly")
    if total_time / total_questions > 30:
        recommendations.append("Practice to improve speed while maintaining accuracy")
    
    return jsonify({
        'session_id': session_id,
        'accuracy': accuracy,
        'total_time': total_time,
        'avg_time': total_time / total_questions if total_questions > 0 else 0,
        'learning_analysis': learning_analysis,
        'recommendations': recommendations,
        'message': 'Session completed and analyzed'
    })

@app.route('/api/student_progress/<student_id>')
def get_student_progress(student_id):
    """Get comprehensive student progress"""
    sessions = db_manager.get_student_sessions(student_id)
    student = db_manager.get_student_by_id(student_id)
    
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    if not sessions:
        return jsonify({
            'student': student,
            'sessions': [],
            'message': 'No sessions found for this student'
        })
    
    # Calculate overall metrics
    total_sessions = len(sessions)
    total_questions = sum(s['questions_asked'] for s in sessions)
    total_correct = sum(s['correct_answers'] for s in sessions)
    overall_accuracy = total_correct / total_questions if total_questions > 0 else 0
    
    # Get learning analysis
    learning_analysis = learning_engine.analyze_learning_style(student_id, {})
    
    # Generate visualization
    visualization = learning_engine.generate_progress_visualization(student_id)
    
    return jsonify({
        'student': student,
        'sessions': sessions,
        'total_sessions': total_sessions,
        'total_questions': total_questions,
        'overall_accuracy': overall_accuracy,
        'learning_analysis': learning_analysis,
        'visualization': visualization
    })

@app.route('/api/dashboard')
def get_dashboard():
    """Get dashboard data for all students"""
    students = db_manager.get_all_students()
    dashboard_data = []
    
    for student in students:
        sessions = db_manager.get_student_sessions(student['id'])
        
        # Calculate student metrics
        total_sessions = len(sessions)
        if sessions:
            recent_accuracy = sessions[0]['correct_answers'] / sessions[0]['questions_asked'] if sessions[0]['questions_asked'] > 0 else 0
            avg_engagement = np.mean([s['engagement_score'] for s in sessions])
        else:
            recent_accuracy = 0
            avg_engagement = 0
        
        # Get learning analysis
        learning_analysis = learning_engine.analyze_learning_style(student['id'], {})
        
        dashboard_data.append({
            'id': student['id'],
            'name': student['name'],
            'age': student['age'],
            'grade': student['grade'],
            'learning_disabilities': student['learning_disabilities'],
            'learning_preferences': student['learning_preferences'],  # Use the original field
            'total_sessions': total_sessions,
            'recent_accuracy': recent_accuracy,
            'avg_engagement': avg_engagement,
            'learning_style': learning_analysis['dominant'],  # Keep for compatibility
            'confidence': learning_analysis['confidence']
        })
    
    return jsonify({'dashboard': dashboard_data})

@app.route('/api/analytics')
def get_analytics():
    """Get comprehensive analytics data"""
    students = db_manager.get_all_students()
    
    # Calculate overall metrics
    total_students = len(students)
    total_sessions = sum(len(db_manager.get_student_sessions(s['id'])) for s in students)
    
    # Calculate average performance
    all_sessions = []
    for student in students:
        sessions = db_manager.get_student_sessions(student['id'])
        all_sessions.extend(sessions)
    
    if all_sessions:
        avg_accuracy = np.mean([s['correct_answers'] / s['questions_asked'] for s in all_sessions if s['questions_asked'] > 0])
        avg_session_time = np.mean([s['total_time'] for s in all_sessions])
    else:
        avg_accuracy = 0
        avg_session_time = 0
    
    # Learning styles distribution
    learning_styles = {}
    for student in students:
        analysis = learning_engine.analyze_learning_style(student['id'], {})
        style = analysis['dominant']
        learning_styles[style] = learning_styles.get(style, 0) + 1
    
    return jsonify({
        'analytics': {
            'total_students': total_students,
            'total_sessions': total_sessions,
            'avg_accuracy': avg_accuracy,
            'avg_session_time': avg_session_time,
            'learning_styles': learning_styles,
            'active_students': len([s for s in students if len(db_manager.get_student_sessions(s['id'])) > 0])
        }
    })

@app.route('/api/settings', methods=['GET', 'POST'])
def handle_settings():
    """Handle settings management"""
    if request.method == 'POST':
        settings = request.json
        # Save settings to database or file
        return jsonify({'success': True, 'message': 'Settings saved successfully'})
    else:
        # Return current settings
        return jsonify({
            'settings': {
                'systemName': 'NeuroLearn',
                'language': 'en',
                'timezone': 'UTC',
                'theme': 'light'
            }
        })

@app.route('/api/profile', methods=['GET', 'POST'])
def handle_profile():
    """Handle profile management"""
    if request.method == 'POST':
        profile = request.json
        # Save profile to database
        return jsonify({'success': True, 'message': 'Profile updated successfully'})
    else:
        # Return current profile
        return jsonify({
            'profile': {
                'firstName': 'Admin',
                'lastName': 'User',
                'email': 'admin@neurolearn.com',
                'phone': '+1 (555) 123-4567',
                'organization': 'NeuroLearn Academy',
                'position': 'System Administrator'
            }
        })

@app.route('/api/change-password', methods=['POST'])
def change_password():
    """Handle password change"""
    data = request.json
    current_password = data.get('currentPassword')
    new_password = data.get('newPassword')
    
    # Validate password change
    if not current_password or not new_password:
        return jsonify({'success': False, 'message': 'Missing password fields'})
    
    if len(new_password) < 8:
        return jsonify({'success': False, 'message': 'Password must be at least 8 characters'})
    
    # In a real app, you would validate current password and update
    return jsonify({'success': True, 'message': 'Password changed successfully'})

@app.route('/api/export-data')
def export_data():
    """Export all data"""
    students = db_manager.get_all_students()
    all_sessions = []
    
    for student in students:
        sessions = db_manager.get_student_sessions(student['id'])
        all_sessions.extend(sessions)
    
    # Create export data
    export_data = {
        'students': students,
        'sessions': all_sessions,
        'export_date': datetime.now().isoformat()
    }
    
    # In a real app, you would create a proper file
    return jsonify(export_data)

@app.route('/api/backup', methods=['POST'])
def create_backup():
    """Create system backup"""
    # In a real app, you would create a proper backup
    return jsonify({'success': True, 'message': 'Backup created successfully'})

@app.route('/api/clear-data', methods=['POST'])
def clear_data():
    """Clear all data"""
    # In a real app, you would clear the database
    return jsonify({'success': True, 'message': 'All data cleared successfully'})

@app.route('/api/test-connection')
def test_connection():
    """Test system connection"""
    return jsonify({'success': True, 'message': 'Connection test successful'})

@app.route('/api/students', methods=['POST'])
def add_student():
    """Add a new student"""
    data = request.json
    
    # Validate required fields
    required_fields = ['name', 'email', 'age', 'learning_style', 'grade_level']
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'message': f'Missing required field: {field}'})
    
    # Create student data
    student_data = {
        'id': f'student_{uuid.uuid4().hex[:8]}',
        'name': data['name'],
        'age': data['age'],
        'grade': data['grade_level'],
        'learning_preferences': [data['learning_style']],
        'subjects': ['math', 'science', 'english'],
        'learning_disabilities': [],
        'interests': [],
        'created_at': datetime.now().isoformat()
    }
    
    # Save to database
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO students (id, name, age, grade, learning_preferences, subjects, learning_disabilities, interests, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        student_data['id'],
        student_data['name'],
        student_data['age'],
        student_data['grade'],
        json.dumps(student_data['learning_preferences']),
        json.dumps(student_data['subjects']),
        json.dumps(student_data['learning_disabilities']),
        json.dumps(student_data['interests']),
        student_data['created_at']
    ))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Student added successfully', 'student': student_data})

@app.route('/api/students/<student_id>', methods=['DELETE'])
def delete_student(student_id):
    """Delete a student"""
    # Delete from database
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM students WHERE id = ?', (student_id,))
    cursor.execute('DELETE FROM sessions WHERE student_id = ?', (student_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Student deleted successfully'})

@app.route('/api/recent_sessions')
def get_recent_sessions():
    """Get recent sessions for display"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Get recent sessions with student names
        cursor.execute('''
            SELECT s.id, s.student_id, st.name as student_name, s.subject, s.questions_asked, 
                   s.correct_answers, s.total_time, s.created_at
            FROM sessions s
            JOIN students st ON s.student_id = st.id
            ORDER BY s.created_at DESC
            LIMIT 10
        ''')
        
        sessions = []
        for row in cursor.fetchall():
            session_id, student_id, student_name, subject, questions_asked, correct_answers, total_time, created_at = row
            
            # Calculate accuracy
            accuracy = round((correct_answers / questions_asked * 100), 1) if questions_asked > 0 else 0
            
            # Format duration
            minutes = int(total_time // 60) if total_time else 0
            seconds = int(total_time % 60) if total_time else 0
            duration = f"{minutes}:{seconds:02d}"
            
            sessions.append({
                'id': session_id,
                'student_id': student_id,
                'student_name': student_name,
                'subject': subject,
                'accuracy': accuracy,
                'duration': duration,
                'date': created_at
            })
        
        conn.close()
        return jsonify({'success': True, 'sessions': sessions})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/session_stats')
def get_session_stats():
    """Get session statistics"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Get total sessions
        cursor.execute('SELECT COUNT(*) FROM sessions')
        total_sessions = cursor.fetchone()[0]
        
        # Get average accuracy
        cursor.execute('''
            SELECT AVG(CAST(correct_answers AS FLOAT) / CAST(questions_asked AS FLOAT) * 100) 
            FROM sessions 
            WHERE questions_asked > 0
        ''')
        avg_accuracy = cursor.fetchone()[0] or 0
        
        # Get average duration
        cursor.execute('SELECT AVG(total_time) FROM sessions WHERE total_time IS NOT NULL')
        avg_duration = cursor.fetchone()[0] or 0
        avg_duration = int(avg_duration // 60) if avg_duration else 0
        
        # Get active students (students with sessions in last 30 days)
        cursor.execute('''
            SELECT COUNT(DISTINCT student_id) FROM sessions 
            WHERE created_at >= datetime('now', '-30 days')
        ''')
        active_students = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'total_sessions': total_sessions,
            'avg_accuracy': round(avg_accuracy, 1),
            'avg_duration': avg_duration,
            'active_students': active_students
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/subject_performance')
def get_subject_performance():
    """Get performance by subject"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Get average accuracy by subject
        cursor.execute('''
            SELECT subject, AVG(CAST(correct_answers AS FLOAT) / CAST(questions_asked AS FLOAT) * 100) as avg_accuracy
            FROM sessions 
            WHERE questions_asked > 0
            GROUP BY subject
            ORDER BY avg_accuracy DESC
        ''')
        
        subjects = []
        accuracies = []
        for row in cursor.fetchall():
            subject, avg_acc = row
            subjects.append(subject.capitalize())
            accuracies.append(round(avg_acc, 1))
        
        # If no data, provide defaults
        if not subjects:
            subjects = ['Math', 'Science', 'English', 'History']
            accuracies = [0, 0, 0, 0]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'subjects': subjects,
            'accuracies': accuracies
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/performance_trends')
def get_performance_trends():
    """Get performance trends over time"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Get performance data for last 6 months
        cursor.execute('''
            SELECT strftime('%Y-%m', created_at) as month,
                   AVG(CAST(correct_answers AS FLOAT) / CAST(questions_asked AS FLOAT) * 100) as avg_accuracy
            FROM sessions 
            WHERE questions_asked > 0 
            AND created_at >= datetime('now', '-6 months')
            GROUP BY month
            ORDER BY month
        ''')
        
        results = cursor.fetchall()
        
        if results:
            labels = []
            data = []
            for month, accuracy in results:
                # Format month label
                date_obj = datetime.strptime(month, '%Y-%m')
                labels.append(date_obj.strftime('%b %Y'))
                data.append(round(accuracy, 1))
        else:
            # If no data, provide empty trend
            labels = ['No data']
            data = [0]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'labels': labels,
                'data': data
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/student_sessions/<student_id>')
def get_student_sessions(student_id):
    """Get sessions for a specific student"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, subject, questions_asked, correct_answers, total_time, created_at
            FROM sessions 
            WHERE student_id = ?
            ORDER BY created_at DESC
            LIMIT 10
        ''', (student_id,))
        
        sessions = []
        for row in cursor.fetchall():
            session_id, subject, questions_asked, correct_answers, total_time, created_at = row
            sessions.append({
                'id': session_id,
                'subject': subject,
                'questions_asked': questions_asked,
                'correct_answers': correct_answers,
                'total_time': total_time,
                'created_at': created_at
            })
        
        conn.close()
        return jsonify({'success': True, 'sessions': sessions})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/student_performance/<student_id>')
def get_student_performance(student_id):
    """Get performance data for a specific student"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Get performance data for last 4 weeks
        cursor.execute('''
            SELECT strftime('%Y-%m-%d', created_at) as date,
                   AVG(CAST(correct_answers AS FLOAT) / CAST(questions_asked AS FLOAT) * 100) as avg_accuracy
            FROM sessions 
            WHERE student_id = ? AND questions_asked > 0 
            AND created_at >= datetime('now', '-4 weeks')
            GROUP BY date
            ORDER BY date
        ''', (student_id,))
        
        results = cursor.fetchall()
        
        if results:
            labels = []
            data = []
            for date, accuracy in results:
                # Format date label
                date_obj = datetime.strptime(date, '%Y-%m-%d')
                labels.append(date_obj.strftime('%b %d'))
                data.append(round(accuracy, 1))
        else:
            # If no data, provide empty trend
            labels = ['No data']
            data = [0]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'labels': labels,
                'data': data
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# OpenVINO-specific API endpoints
@app.route('/api/openvino/status')
def get_openvino_status():
    """Get OpenVINO system status and model information"""
    try:
        from openvino_utils import OpenVINOLearningAnalyzer
        
        analyzer = OpenVINOLearningAnalyzer()
        status = analyzer.get_openvino_status()
        
        return jsonify({
            'success': True,
            'openvino_status': status,
            'message': 'OpenVINO status retrieved successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/openvino/benchmark')
def benchmark_openvino():
    """Benchmark OpenVINO performance"""
    try:
        from openvino_utils import OpenVINOLearningAnalyzer
        
        analyzer = OpenVINOLearningAnalyzer()
        analyzer.initialize_models()
        benchmark_results = analyzer.benchmark_performance()
        
        return jsonify({
            'success': True,
            'benchmark': benchmark_results,
            'message': 'OpenVINO benchmark completed'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/openvino/analyze_learning_style', methods=['POST'])
def analyze_learning_style_openvino():
    """Analyze learning style using OpenVINO"""
    try:
        data = request.get_json()
        interaction_data = data.get('interaction_data', [])
        
        if not interaction_data:
            return jsonify({'success': False, 'error': 'No interaction data provided'}), 400
        
        from openvino_utils import OpenVINOLearningAnalyzer
        
        analyzer = OpenVINOLearningAnalyzer()
        analyzer.initialize_models()
        
        analysis = analyzer.analyze_learning_patterns(interaction_data)
        
        return jsonify({
            'success': True,
            'analysis': analysis,
            'message': 'Learning style analysis completed using OpenVINO'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/openvino/predict_performance', methods=['POST'])
def predict_performance_openvino():
    """Predict performance using OpenVINO"""
    try:
        data = request.get_json()
        historical_data = data.get('historical_data', [])
        
        if not historical_data:
            return jsonify({'success': False, 'error': 'No historical data provided'}), 400
        
        from openvino_utils import OpenVINOLearningAnalyzer
        
        analyzer = OpenVINOLearningAnalyzer()
        analyzer.initialize_models()
        
        prediction = analyzer.predict_performance(historical_data)
        
        return jsonify({
            'success': True,
            'prediction': prediction,
            'message': 'Performance prediction completed using OpenVINO'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/openvino/optimize_content', methods=['POST'])
def optimize_content_openvino():
    """Optimize content delivery using OpenVINO"""
    try:
        data = request.get_json()
        learning_style = data.get('learning_style', 'visual')
        current_performance = data.get('current_performance', 0.5)
        session_time = data.get('session_time', 0.5)
        engagement = data.get('engagement', 0.7)
        
        from openvino_utils import OpenVINOLearningAnalyzer
        
        analyzer = OpenVINOLearningAnalyzer()
        analyzer.initialize_models()
        
        optimization = analyzer.optimize_content_delivery(
            learning_style, current_performance, session_time, engagement
        )
        
        return jsonify({
            'success': True,
            'optimization': optimization,
            'message': 'Content optimization completed using OpenVINO'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/openvino/demo')
def openvino_demo():
    """Run a comprehensive OpenVINO demo"""
    try:
        from openvino_utils import OpenVINOLearningAnalyzer
        
        analyzer = OpenVINOLearningAnalyzer()
        analyzer.initialize_models()
        
        # Demo data
        interaction_data = [0.8, 0.6, 0.4, 0.7, 0.5, 0.3, 0.9, 0.2, 0.6, 0.8]
        historical_data = [0.6, 0.7, 0.8, 0.75, 0.85]
        
        # Run all analyses
        learning_analysis = analyzer.analyze_learning_patterns(interaction_data)
        performance_prediction = analyzer.predict_performance(historical_data)
        content_optimization = analyzer.optimize_content_delivery(
            learning_analysis['dominant'], 
            learning_analysis['confidence'], 
            0.6, 0.8
        )
        benchmark = analyzer.benchmark_performance()
        status = analyzer.get_openvino_status()
        
        return jsonify({
            'success': True,
            'demo_results': {
                'learning_analysis': learning_analysis,
                'performance_prediction': performance_prediction,
                'content_optimization': content_optimization,
                'benchmark': benchmark,
                'status': status
            },
            'message': 'OpenVINO demo completed successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 