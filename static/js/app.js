// NeuroLearn Frontend JavaScript
class NeuroLearnApp {
    constructor() {
        this.currentStudentId = null;
        this.sessionCount = 0;
        this.students = [];
        console.log('NeuroLearnApp: Initializing...');
        this.initializeEventListeners();
        this.loadStudents();
        this.loadDashboard();
    }

    initializeEventListeners() {
        // Student form submission
        document.getElementById('studentForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.startLearningSession();
        });

        // Complete session button
        document.getElementById('completeSession').addEventListener('click', () => {
            this.completeLearningSession();
        });

        // Self test form submission
        document.getElementById('selfTestForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.startSelfTest();
        });
    }

    async startLearningSession() {
        const studentId = document.getElementById('studentId').value;
        const contentType = document.getElementById('contentType').value;
        const difficulty = document.getElementById('difficulty').value;

        this.currentStudentId = studentId;
        this.sessionCount++;

        // Show loading modal
        const modal = new bootstrap.Modal(document.getElementById('learningModal'));
        modal.show();

        try {
            // Analyze learning patterns
            const analysisResponse = await this.analyzeLearning(studentId);
            
            // Adapt content based on learning style
            const adaptationResponse = await this.adaptContent(studentId, contentType, difficulty);
            
            // Update UI with results
            this.updateLearningInterface(analysisResponse, adaptationResponse);
            
        } catch (error) {
            console.error('Error starting learning session:', error);
            this.showError('Failed to start learning session. Please try again.');
        }
    }

    async analyzeLearning(studentId) {
        const response = await fetch('/api/analyze_learning', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                student_id: studentId,
                interaction_data: this.generateInteractionData()
            })
        });

        if (!response.ok) {
            throw new Error('Failed to analyze learning patterns');
        }

        return await response.json();
    }

    async adaptContent(studentId, contentType, difficulty) {
        const response = await fetch('/api/adapt_content', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                student_id: studentId,
                content_type: contentType,
                current_difficulty: difficulty
            })
        });

        if (!response.ok) {
            throw new Error('Failed to adapt content');
        }

        return await response.json();
    }

    generateInteractionData() {
        // Simulate realistic interaction data
        return [
            Math.random() * 0.8 + 0.2,  // Visual engagement (0.2-1.0)
            Math.random() * 0.8 + 0.2,  // Auditory engagement (0.2-1.0)
            Math.random() * 0.8 + 0.2,  // Kinesthetic engagement (0.2-1.0)
            Math.random() * 0.6 + 0.4,  // Performance score (0.4-1.0)
            Math.random() * 0.5 + 0.3   // Time spent (0.3-0.8)
        ];
    }

    updateLearningInterface(analysisResponse, adaptationResponse) {
        const sessionContent = document.getElementById('sessionContent');
        const learningStyleResults = document.getElementById('learningStyleResults');
        const learningContent = document.getElementById('learningContent');

        // Update learning style analysis
        if (analysisResponse.learning_style) {
            const style = analysisResponse.learning_style;
            learningStyleResults.innerHTML = `
                <div class="fade-in">
                    <h6>Learning Style Analysis</h6>
                    <div class="mb-2">
                        <span class="learning-style-indicator ${style.dominant}-style">
                            ${style.dominant.charAt(0).toUpperCase() + style.dominant.slice(1)} Learner
                        </span>
                    </div>
                    <div class="progress mb-2">
                        <div class="progress-bar bg-primary" style="width: ${(style.visual * 100).toFixed(1)}%"></div>
                    </div>
                    <small class="text-muted">Visual: ${(style.visual * 100).toFixed(1)}%</small>
                    
                    <div class="progress mb-2">
                        <div class="progress-bar bg-success" style="width: ${(style.auditory * 100).toFixed(1)}%"></div>
                    </div>
                    <small class="text-muted">Auditory: ${(style.auditory * 100).toFixed(1)}%</small>
                    
                    <div class="progress mb-2">
                        <div class="progress-bar bg-danger" style="width: ${(style.kinesthetic * 100).toFixed(1)}%"></div>
                    </div>
                    <small class="text-muted">Kinesthetic: ${(style.kinesthetic * 100).toFixed(1)}%</small>
                </div>
            `;
        }

        // Update session content
        const adaptation = adaptationResponse.adaptation;
        sessionContent.innerHTML = `
            <div class="fade-in">
                <div class="alert alert-info">
                    <i class="fas fa-brain me-2"></i>
                    <strong>AI Analysis Complete!</strong>
                    <br>
                    ${adaptation.adaptation}
                </div>
                
                <div class="row">
                    <div class="col-md-6">
                        <h6><i class="fas fa-cog me-2"></i>Content Adaptation</h6>
                        <ul class="list-unstyled">
                            <li><i class="fas fa-check text-success me-2"></i>Difficulty: ${adaptation.difficulty}</li>
                            <li><i class="fas fa-check text-success me-2"></i>Style: ${adaptation.learning_style}</li>
                            <li><i class="fas fa-check text-success me-2"></i>Personalized content loaded</li>
                        </ul>
                    </div>
                    <div class="col-md-6">
                        <h6><i class="fas fa-chart-line me-2"></i>Session Progress</h6>
                        <div class="progress mb-2">
                            <div class="progress-bar bg-warning" style="width: 75%"></div>
                        </div>
                        <small class="text-muted">75% Complete</small>
                    </div>
                </div>
                
                <div class="mt-3">
                    <h6><i class="fas fa-lightbulb me-2"></i>Recommended Activities</h6>
                    <div class="row">
                        <div class="col-md-4">
                            <div class="card bg-light">
                                <div class="card-body text-center">
                                    <i class="fas fa-eye fa-2x text-primary mb-2"></i>
                                    <h6>Visual Learning</h6>
                                    <small class="text-muted">Interactive diagrams and charts</small>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="card bg-light">
                                <div class="card-body text-center">
                                    <i class="fas fa-volume-up fa-2x text-success mb-2"></i>
                                    <h6>Audio Learning</h6>
                                    <small class="text-muted">Narrated explanations</small>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="card bg-light">
                                <div class="card-body text-center">
                                    <i class="fas fa-hands-helping fa-2x text-danger mb-2"></i>
                                    <h6>Hands-on</h6>
                                    <small class="text-muted">Interactive simulations</small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Update main learning content
        learningContent.innerHTML = `
            <div class="fade-in">
                <div class="alert alert-success">
                    <i class="fas fa-graduation-cap me-2"></i>
                    <strong>Learning Session Active</strong>
                    <br>
                    Content has been adapted for ${adaptation.learning_style} learners at ${adaptation.difficulty} difficulty level.
                </div>
                
                <div class="row">
                    <div class="col-md-8">
                        <h5><i class="fas fa-book me-2"></i>Adaptive Content</h5>
                        <div class="card bg-light">
                            <div class="card-body">
                                <h6>Mathematics - ${adaptation.difficulty.charAt(0).toUpperCase() + adaptation.difficulty.slice(1)} Level</h6>
                                <p>This content has been personalized based on your learning style. The AI has analyzed your interaction patterns and adjusted the difficulty and presentation method accordingly.</p>
                                
                                <div class="mt-3">
                                    <button class="btn btn-primary me-2">
                                        <i class="fas fa-play me-2"></i>Start Exercise
                                    </button>
                                    <button class="btn btn-outline-secondary">
                                        <i class="fas fa-info-circle me-2"></i>View Explanation
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <h5><i class="fas fa-trophy me-2"></i>Progress</h5>
                        <div class="text-center">
                            <div class="display-4 text-primary">${this.sessionCount}</div>
                            <small class="text-muted">Learning Sessions</small>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    async completeLearningSession() {
        if (!this.currentStudentId) return;

        try {
            // Get visualization
            const vizResponse = await this.getVisualization(this.currentStudentId);
            
            // Get progress report
            const progressResponse = await this.getProgressReport(this.currentStudentId);
            
            // Update UI with results
            this.updateProgressDisplay(vizResponse, progressResponse);
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('learningModal'));
            modal.hide();
            
        } catch (error) {
            console.error('Error completing session:', error);
            this.showError('Failed to complete session. Please try again.');
        }
    }

    async getVisualization(studentId) {
        const response = await fetch(`/api/visualization/${studentId}`);
        if (!response.ok) {
            throw new Error('Failed to get visualization');
        }
        return await response.json();
    }

    async getProgressReport(studentId) {
        const response = await fetch(`/api/student_progress/${studentId}`);
        if (!response.ok) {
            throw new Error('Failed to get progress report');
        }
        return await response.json();
    }

    updateProgressDisplay(vizResponse, progressResponse) {
        // Update visualization
        const vizContainer = document.getElementById('visualizationContainer');
        if (vizResponse.visualization) {
            vizContainer.innerHTML = `
                <div class="fade-in">
                    <img src="data:image/png;base64,${vizResponse.visualization}" 
                         alt="Learning Progress Visualization" 
                         class="img-fluid">
                </div>
            `;
        } else {
            vizContainer.innerHTML = `
                <div class="alert alert-info">
                    <i class="fas fa-info-circle me-2"></i>
                    Complete more learning sessions to see detailed visualizations.
                </div>
            `;
        }

        // Update progress report
        const progressReport = document.getElementById('progressReport');
        if (progressResponse.total_sessions) {
            progressReport.innerHTML = `
                <div class="fade-in">
                    <div class="row">
                        <div class="col-md-3">
                            <div class="text-center">
                                <div class="display-6 text-primary">${progressResponse.total_sessions}</div>
                                <small class="text-muted">Total Sessions</small>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="text-center">
                                <div class="display-6 text-success">${(progressResponse.average_performance * 100).toFixed(1)}%</div>
                                <small class="text-muted">Average Performance</small>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="text-center">
                                <div class="display-6 text-warning">${(progressResponse.engagement_score * 100).toFixed(1)}%</div>
                                <small class="text-muted">Engagement Score</small>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="text-center">
                                <div class="display-6 text-info">${(progressResponse.improvement_rate * 100).toFixed(1)}%</div>
                                <small class="text-muted">Improvement Rate</small>
                            </div>
                        </div>
                    </div>
                    
                    ${progressResponse.recommendations.length > 0 ? `
                        <div class="mt-4">
                            <h6><i class="fas fa-lightbulb me-2"></i>AI Recommendations</h6>
                            <ul class="list-unstyled">
                                ${progressResponse.recommendations.map(rec => `
                                    <li><i class="fas fa-arrow-right text-primary me-2"></i>${rec}</li>
                                `).join('')}
                            </ul>
                        </div>
                    ` : ''}
                </div>
            `;
        } else {
            progressReport.innerHTML = `
                <div class="alert alert-info">
                    <i class="fas fa-info-circle me-2"></i>
                    ${progressResponse.message}
                </div>
            `;
        }
    }

    async loadStudents() {
        try {
            // Fetch students from backend (replace with real DB/API in production)
            const res = await fetch('/api/students');
            if (!res.ok) {
                throw new Error(`HTTP ${res.status}: ${res.statusText}`);
            }
            const data = await res.json();
            this.students = data.students;
            this.populateStudentDropdown();
        } catch (error) {
            console.error('Error loading students:', error);
            this.showError('Failed to load students: ' + error.message);
        }
    }

    populateStudentDropdown() {
        const studentIdInput = document.getElementById('studentId');
        if (!studentIdInput) return;
        // Remove existing options
        studentIdInput.innerHTML = '';
        this.students.forEach(stu => {
            const opt = document.createElement('option');
            opt.value = stu.id;
            opt.textContent = `${stu.name} (${stu.id})`;
            studentIdInput.appendChild(opt);
        });
    }

    async loadDashboard() {
        try {
            // Fetch dashboard data (replace with real analytics in production)
            const res = await fetch('/api/dashboard');
            if (!res.ok) {
                throw new Error(`HTTP ${res.status}: ${res.statusText}`);
            }
            const data = await res.json();
            this.renderDashboard(data.dashboard);
        } catch (error) {
            console.error('Error loading dashboard:', error);
            this.showError('Failed to load dashboard: ' + error.message);
        }
    }

    renderDashboard(dashboard) {
        // Add a simple dashboard table below the main content
        let dashHtml = `<h5 class='mt-4 mb-2'><i class='fas fa-chalkboard-teacher me-2'></i>Classroom Dashboard</h5>`;
        dashHtml += `<div class='table-responsive'><table class='table table-bordered table-striped'><thead><tr><th>Name</th><th>Background</th><th>Disabilities</th><th>Pace</th><th>Sessions</th><th>Last Style</th><th>Avg Perf</th><th>Notes</th><th>Actions</th></tr></thead><tbody>`;
        dashboard.forEach(stu => {
            dashHtml += `<tr>
                <td>${stu.name}</td>
                <td>${stu.background}</td>
                <td>${stu.disabilities.join(', ') || '-'}</td>
                <td>${stu.pace}</td>
                <td>${stu.total_sessions}</td>
                <td>${stu.last_learning_style || '-'}</td>
                <td>${stu.average_performance !== null ? (stu.average_performance*100).toFixed(1)+'%' : '-'}</td>
                <td>${stu.notes}</td>
                <td>
                    <button class='btn btn-sm btn-primary' onclick='app.startSessionForStudent("${stu.id}")'>
                        <i class='fas fa-play me-1'></i>Start Session
                    </button>
                    <button class='btn btn-sm btn-info' onclick='app.viewStudentAnalytics("${stu.id}")'>
                        <i class='fas fa-chart-line me-1'></i>Analytics
                    </button>
                </td>
            </tr>`;
        });
        dashHtml += `</tbody></table></div>`;
        // Place dashboard at the end of the main container
        let container = document.querySelector('.container');
        let dashDiv = document.getElementById('dashboardSection');
        if (!dashDiv) {
            dashDiv = document.createElement('div');
            dashDiv.id = 'dashboardSection';
            container.appendChild(dashDiv);
        }
        dashDiv.innerHTML = dashHtml;
    }

    async startSessionForStudent(studentId) {
        // Start a learning session for the selected student
        const subject = document.getElementById('contentType').value;
        try {
            const response = await fetch('/api/start_session', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    student_id: studentId,
                    subject: subject,
                    num_questions: 2
                })
            });
            const data = await response.json();
            this.showSessionResults(studentId, data);
        } catch (error) {
            console.error('Error starting session:', error);
            this.showError('Failed to start session');
        }
    }

    showSessionResults(studentId, sessionData) {
        // Show session results in a modal
        const modal = new bootstrap.Modal(document.getElementById('learningModal'));
        const sessionContent = document.getElementById('sessionContent');
        
        let resultsHtml = `
            <div class='fade-in'>
                <div class='alert alert-success'>
                    <i class='fas fa-check-circle me-2'></i>
                    <strong>Session Completed!</strong>
                    <br>Student: ${this.students.find(s => s.id === studentId)?.name || studentId}
                </div>
                
                <h6><i class='fas fa-question-circle me-2'></i>Session Results</h6>
                <div class='row'>`;
        
        sessionData.results.forEach((result, index) => {
            const isCorrect = result.correct;
            const badgeClass = isCorrect ? 'success' : 'danger';
            const icon = isCorrect ? 'check' : 'times';
            
            resultsHtml += `
                <div class='col-md-6 mb-3'>
                    <div class='card ${isCorrect ? 'border-success' : 'border-danger'}'>
                        <div class='card-body'>
                            <h6>Question ${index + 1}</h6>
                            <p class='mb-2'>${result.question}</p>
                            <div class='d-flex justify-content-between align-items-center'>
                                <span class='badge bg-${badgeClass}'>
                                    <i class='fas fa-${icon} me-1'></i>
                                    ${isCorrect ? 'Correct' : 'Incorrect'}
                                </span>
                                <small class='text-muted'>
                                    <i class='fas fa-clock me-1'></i>${result.time_taken}s
                                </small>
                            </div>
                            <div class='mt-2'>
                                <small class='text-muted'>Selected: ${result.selected}</small>
                            </div>
                        </div>
                    </div>
                </div>`;
        });
        
        const correctCount = sessionData.results.filter(r => r.correct).length;
        const totalQuestions = sessionData.results.length;
        const accuracy = (correctCount / totalQuestions * 100).toFixed(1);
        
        resultsHtml += `
                </div>
                <div class='row mt-3'>
                    <div class='col-md-4'>
                        <div class='text-center'>
                            <div class='display-6 text-primary'>${accuracy}%</div>
                            <small class='text-muted'>Accuracy</small>
                        </div>
                    </div>
                    <div class='col-md-4'>
                        <div class='text-center'>
                            <div class='display-6 text-success'>${correctCount}/${totalQuestions}</div>
                            <small class='text-muted'>Correct Answers</small>
                        </div>
                    </div>
                    <div class='col-md-4'>
                        <div class='text-center'>
                            <div class='display-6 text-warning'>${(sessionData.results.reduce((sum, r) => sum + r.time_taken, 0) / totalQuestions).toFixed(1)}s</div>
                            <small class='text-muted'>Avg Time</small>
                        </div>
                    </div>
                </div>
            </div>`;
        
        sessionContent.innerHTML = resultsHtml;
        modal.show();
        
        // Refresh dashboard after session
        setTimeout(() => {
            this.loadDashboard();
        }, 1000);
    }

    async viewStudentAnalytics(studentId) {
        try {
            // Get session results
            const response = await fetch(`/api/session_results/${studentId}`);
            const data = await response.json();
            
            // Get student profile
            const student = this.students.find(s => s.id === studentId);
            
            // Get progress report
            const progressResponse = await fetch(`/api/student_progress/${studentId}`);
            const progressData = await progressResponse.json();
            
            this.showStudentAnalytics(student, data.sessions, progressData);
        } catch (error) {
            console.error('Error loading analytics:', error);
            this.showError('Failed to load analytics');
        }
    }

    showStudentAnalytics(student, sessions, progress) {
        const modal = new bootstrap.Modal(document.getElementById('learningModal'));
        const sessionContent = document.getElementById('sessionContent');
        
        let analyticsHtml = `
            <div class='fade-in'>
                <div class='alert alert-info'>
                    <i class='fas fa-user-graduate me-2'></i>
                    <strong>Student Analytics</strong>
                    <br>${student.name} (${student.id})
                </div>
                
                <div class='row'>
                    <div class='col-md-6'>
                        <h6><i class='fas fa-info-circle me-2'></i>Profile</h6>
                        <ul class='list-unstyled'>
                            <li><strong>Age:</strong> ${student.age}</li>
                            <li><strong>Background:</strong> ${student.background}</li>
                            <li><strong>Disabilities:</strong> ${student.disabilities.join(', ') || 'None'}</li>
                            <li><strong>Learning Pace:</strong> ${student.pace}</li>
                            <li><strong>Notes:</strong> ${student.notes}</li>
                        </ul>
                    </div>
                    <div class='col-md-6'>
                        <h6><i class='fas fa-chart-bar me-2'></i>Performance Summary</h6>
                        <ul class='list-unstyled'>
                            <li><strong>Total Sessions:</strong> ${sessions.length}</li>
                            <li><strong>Average Performance:</strong> ${progress.average_performance ? (progress.average_performance * 100).toFixed(1) + '%' : 'N/A'}</li>
                            <li><strong>Engagement Score:</strong> ${progress.engagement_score ? (progress.engagement_score * 100).toFixed(1) + '%' : 'N/A'}</li>
                            <li><strong>Improvement Rate:</strong> ${progress.improvement_rate ? (progress.improvement_rate * 100).toFixed(1) + '%' : 'N/A'}</li>
                        </ul>
                    </div>
                </div>`;
        
        if (sessions.length > 0) {
            analyticsHtml += `
                <div class='mt-4'>
                    <h6><i class='fas fa-history me-2'></i>Session History</h6>
                    <div class='table-responsive'>
                        <table class='table table-sm'>
                            <thead>
                                <tr>
                                    <th>Session</th>
                                    <th>Subject</th>
                                    <th>Accuracy</th>
                                    <th>Avg Time</th>
                                </tr>
                            </thead>
                            <tbody>`;
            
            sessions.forEach((session, index) => {
                const correctCount = session.questions.filter(q => q.correct).length;
                const accuracy = (correctCount / session.questions.length * 100).toFixed(1);
                const avgTime = (session.questions.reduce((sum, q) => sum + q.time_taken, 0) / session.questions.length).toFixed(1);
                
                analyticsHtml += `
                    <tr>
                        <td>${index + 1}</td>
                        <td>${session.subject}</td>
                        <td><span class='badge bg-${accuracy >= 70 ? 'success' : accuracy >= 50 ? 'warning' : 'danger'}'>${accuracy}%</span></td>
                        <td>${avgTime}s</td>
                    </tr>`;
            });
            
            analyticsHtml += `
                            </tbody>
                        </table>
                    </div>
                </div>`;
        }
        
        if (progress.recommendations && progress.recommendations.length > 0) {
            analyticsHtml += `
                <div class='mt-4'>
                    <h6><i class='fas fa-lightbulb me-2'></i>AI Recommendations</h6>
                    <ul class='list-unstyled'>`;
            
            progress.recommendations.forEach(rec => {
                analyticsHtml += `<li><i class='fas fa-arrow-right text-primary me-2'></i>${rec}</li>`;
            });
            
            analyticsHtml += `
                    </ul>
                </div>`;
        }
        
        analyticsHtml += `</div>`;
        
        sessionContent.innerHTML = analyticsHtml;
        modal.show();
    }

    async startSelfTest() {
        const subject = document.getElementById('testSubject').value;
        try {
            // Get questions for the test
            const response = await fetch('/api/get_test_questions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    subject: subject,
                    num_questions: 3
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            this.showTestQuestions(data.questions, subject);
        } catch (error) {
            console.error('Error starting test:', error);
            this.showError('Failed to start test: ' + error.message);
        }
    }

    showTestQuestions(questions, subject) {
        const modal = new bootstrap.Modal(document.getElementById('learningModal'));
        const sessionContent = document.getElementById('sessionContent');
        
        let questionsHtml = `
            <div class='fade-in'>
                <div class='alert alert-info'>
                    <i class='fas fa-question-circle me-2'></i>
                    <strong>Your Test</strong>
                    <br>Subject: ${subject.charAt(0).toUpperCase() + subject.slice(1)}
                </div>
                
                <form id='testForm'>
                    <div class='mb-3'>
                        <small class='text-muted'>Answer the questions below. Your responses will be analyzed for learning patterns.</small>
                    </div>`;
        
        questions.forEach((question, index) => {
            questionsHtml += `
                <div class='card mb-3'>
                    <div class='card-body'>
                        <h6>Question ${index + 1}</h6>
                        <p class='mb-3'>${question.question}</p>
                        <div class='mb-3'>
                            ${question.options.map((option, optIndex) => `
                                <div class='form-check'>
                                    <input class='form-check-input' type='radio' name='q${index}' id='q${index}opt${optIndex}' value='${option}' required>
                                    <label class='form-check-label' for='q${index}opt${optIndex}'>
                                        ${option}
                                    </label>
                                </div>
                            `).join('')}
                        </div>
                        <div class='mb-2'>
                            <small class='text-muted'>Time spent: <span id='time${index}'>0</span> seconds</small>
                        </div>
                    </div>
                </div>`;
        });
        
        questionsHtml += `
                    <div class='text-center'>
                        <button type='submit' class='btn btn-primary'>
                            <i class='fas fa-paper-plane me-2'></i>Submit Test
                        </button>
                    </div>
                </form>
            </div>`;
        
        sessionContent.innerHTML = questionsHtml;
        modal.show();
        
        // Start timing for each question
        this.startQuestionTiming(questions.length);
        
        // Handle form submission
        document.getElementById('testForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitTestAnswers(questions, subject);
        });
    }

    startQuestionTiming(numQuestions) {
        this.questionTimers = [];
        this.questionStartTimes = [];
        
        for (let i = 0; i < numQuestions; i++) {
            this.questionStartTimes[i] = Date.now();
            this.questionTimers[i] = setInterval(() => {
                const timeSpent = Math.floor((Date.now() - this.questionStartTimes[i]) / 1000);
                const timeElement = document.getElementById(`time${i}`);
                if (timeElement) {
                    timeElement.textContent = timeSpent;
                }
            }, 1000);
        }
    }

    async submitTestAnswers(questions, subject) {
        // Stop all timers
        if (this.questionTimers) {
            this.questionTimers.forEach(timer => clearInterval(timer));
        }
        
        // Collect answers and timing
        const answers = [];
        let totalTime = 0;
        
        questions.forEach((question, index) => {
            const selectedAnswer = document.querySelector(`input[name="q${index}"]:checked`);
            const timeSpent = Math.floor((Date.now() - this.questionStartTimes[index]) / 1000);
            totalTime += timeSpent;
            
            answers.push({
                selected: selectedAnswer ? selectedAnswer.value : null,
                time_taken: timeSpent
            });
        });
        
        try {
            const response = await fetch('/api/submit_test_answers', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    answers: answers,
                    subject: subject,
                    time_taken: totalTime
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            this.showTestAnalysis(data.analysis);
        } catch (error) {
            console.error('Error submitting test:', error);
            this.showError('Failed to submit test: ' + error.message);
        }
    }

    showTestAnalysis(analysis) {
        const modal = new bootstrap.Modal(document.getElementById('learningModal'));
        const sessionContent = document.getElementById('sessionContent');
        
        let analysisHtml = `
            <div class='fade-in'>
                <div class='alert alert-success'>
                    <i class='fas fa-chart-line me-2'></i>
                    <strong>Your Learning Analysis</strong>
                    <br>Based on your test performance
                </div>
                
                <div class='row'>
                    <div class='col-md-6'>
                        <h6><i class='fas fa-trophy me-2'></i>Performance Summary</h6>
                        <div class='text-center mb-3'>
                            <div class='display-4 text-primary'>${(analysis.accuracy * 100).toFixed(1)}%</div>
                            <small class='text-muted'>Accuracy</small>
                        </div>
                        <div class='text-center mb-3'>
                            <div class='display-6 text-success'>${analysis.correct_count}/${analysis.total_questions}</div>
                            <small class='text-muted'>Correct Answers</small>
                        </div>
                        <div class='text-center mb-3'>
                            <div class='display-6 text-warning'>${analysis.avg_time.toFixed(1)}s</div>
                            <small class='text-muted'>Average Time per Question</small>
                        </div>
                    </div>
                    <div class='col-md-6'>
                        <h6><i class='fas fa-brain me-2'></i>Learning Style Analysis</h6>
                        <div class='mb-3'>
                            <span class='learning-style-indicator ${analysis.dominant_learning_style}-style'>
                                ${analysis.dominant_learning_style.charAt(0).toUpperCase() + analysis.dominant_learning_style.slice(1)} Learner
                            </span>
                        </div>
                        <div class='progress mb-2'>
                            <div class='progress-bar bg-primary' style='width: ${(analysis.avg_engagement * 100).toFixed(1)}%'></div>
                        </div>
                        <small class='text-muted'>Engagement Level: ${(analysis.avg_engagement * 100).toFixed(1)}%</small>
                    </div>
                </div>`;
        
        if (analysis.recommendations && analysis.recommendations.length > 0) {
            analysisHtml += `
                <div class='mt-4'>
                    <h6><i class='fas fa-lightbulb me-2'></i>Personalized Recommendations</h6>
                    <ul class='list-unstyled'>`;
            
            analysis.recommendations.forEach(rec => {
                analysisHtml += `<li><i class='fas fa-arrow-right text-primary me-2'></i>${rec}</li>`;
            });
            
            analysisHtml += `
                    </ul>
                </div>`;
        }
        
        analysisHtml += `
                <div class='mt-4'>
                    <h6><i class='fas fa-question-circle me-2'></i>Question Results</h6>
                    <div class='row'>`;
        
        analysis.results.forEach((result, index) => {
            const isCorrect = result.correct;
            const badgeClass = isCorrect ? 'success' : 'danger';
            const icon = isCorrect ? 'check' : 'times';
            
            analysisHtml += `
                <div class='col-md-6 mb-2'>
                    <div class='card ${isCorrect ? 'border-success' : 'border-danger'}'>
                        <div class='card-body p-2'>
                            <small><strong>Q${index + 1}:</strong> ${result.question}</small>
                            <div class='d-flex justify-content-between align-items-center mt-1'>
                                <span class='badge bg-${badgeClass}'>
                                    <i class='fas fa-${icon} me-1'></i>
                                    ${isCorrect ? 'Correct' : 'Incorrect'}
                                </span>
                                <small class='text-muted'>${result.time_taken}s</small>
                            </div>
                        </div>
                    </div>
                </div>`;
        });
        
        analysisHtml += `
                    </div>
                </div>
            </div>`;
        
        sessionContent.innerHTML = analysisHtml;
        modal.show();
    }

    showError(message) {
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-danger fade-in';
        alertDiv.innerHTML = `
            <i class="fas fa-exclamation-triangle me-2"></i>
            ${message}
        `;
        
        document.querySelector('.container').insertBefore(alertDiv, document.querySelector('.container').firstChild);
        
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
}

// Initialize the application when DOM is loaded
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new NeuroLearnApp();
}); 