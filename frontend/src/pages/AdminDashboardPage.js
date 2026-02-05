import { API_BASE_URL } from '../utils/api.js';

export function AdminDashboardPage() {
    const container = document.createElement('div');
    container.className = 'admin-dashboard-container';

    // Add Chart.js script if not already loaded
    if (!window.Chart) {
        const chartScript = document.createElement('script');
        chartScript.src = 'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js';
        document.head.appendChild(chartScript);
    }

    container.innerHTML = `
        <div class="admin-dashboard">
            <div class="dashboard-header">
                <h1>Admin Dashboard</h1>
                <button id="refreshBtn" class="btn btn-primary">
                    <i class="fas fa-sync-alt"></i> Refresh
                </button>
            </div>

            <div id="loadingIndicator" class="loading">
                <i class="fas fa-spinner fa-spin"></i> Loading dashboard data...
            </div>

            <div id="dashboardContent" style="display: none;">
                <!-- Statistics Cards -->
                <div class="stats-grid">
                    <div class="stat-card stat-users">
                        <div class="stat-icon">
                            <i class="fas fa-users"></i>
                        </div>
                        <div class="stat-content">
                            <h3 id="totalUsers">0</h3>
                            <p>Total Users</p>
                        </div>
                    </div>

                    <div class="stat-card stat-students">
                        <div class="stat-icon">
                            <i class="fas fa-user-graduate"></i>
                        </div>
                        <div class="stat-content">
                            <h3 id="totalStudents">0</h3>
                            <p>Students</p>
                        </div>
                    </div>

                    <div class="stat-card stat-capsules">
                        <div class="stat-icon">
                            <i class="fas fa-book"></i>
                        </div>
                        <div class="stat-content">
                            <h3 id="totalCapsules">0</h3>
                            <p>Learning Capsules</p>
                        </div>
                    </div>

                    <div class="stat-card stat-quizzes">
                        <div class="stat-icon">
                            <i class="fas fa-clipboard-check"></i>
                        </div>
                        <div class="stat-content">
                            <h3 id="totalQuizzes">0</h3>
                            <p>Total Quizzes</p>
                        </div>
                    </div>

                    <div class="stat-card stat-completion">
                        <div class="stat-icon">
                            <i class="fas fa-chart-line"></i>
                        </div>
                        <div class="stat-content">
                            <h3 id="avgCompletion">0%</h3>
                            <p>Avg. Completion Rate</p>
                        </div>
                    </div>

                    <div class="stat-card stat-quiz-score">
                        <div class="stat-icon">
                            <i class="fas fa-trophy"></i>
                        </div>
                        <div class="stat-content">
                            <h3 id="avgQuizScore">0%</h3>
                            <p>Avg. Quiz Score</p>
                        </div>
                    </div>
                </div>

                <!-- Charts Section -->
                <div class="charts-section">
                    <div class="chart-container">
                        <h2>Subject Distribution</h2>
                        <canvas id="subjectChart"></canvas>
                    </div>

                    <div class="chart-container">
                        <h2>Grade Distribution</h2>
                        <canvas id="gradeChart"></canvas>
                    </div>

                    <div class="chart-container full-width">
                        <h2>User Engagement Overview</h2>
                        <canvas id="engagementChart"></canvas>
                    </div>
                </div>

                <!-- Users Table -->
                <div class="users-section">
                    <div class="section-header">
                        <h2>All Users</h2>
                        <div class="search-box">
                            <i class="fas fa-search"></i>
                            <input type="text" id="userSearch" placeholder="Search users...">
                        </div>
                    </div>

                    <div class="table-container">
                        <table class="users-table">
                            <thead>
                                <tr>
                                    <th>Username</th>
                                    <th>Email</th>
                                    <th>Role</th>
                                    <th>Joined</th>
                                    <th>Last Login</th>
                                    <th>Capsules</th>
                                    <th>Quizzes</th>
                                    <th>Avg Score</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody id="usersTableBody">
                                <tr>
                                    <td colspan="9" style="text-align: center;">Loading...</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- Recent Activity -->
                <div class="activity-section">
                    <h2>Recent Quiz Attempts</h2>
                    <div id="recentActivity" class="activity-list">
                        <p>Loading recent activity...</p>
                    </div>
                </div>
            </div>
        </div>

        <style>
            .admin-dashboard-container {
                padding: 20px;
                max-width: 1400px;
                margin: 0 auto;
            }

            .dashboard-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 30px;
            }

            .dashboard-header h1 {
                color: #2c3e50;
                margin: 0;
            }

            .loading {
                text-align: center;
                padding: 60px;
                font-size: 18px;
                color: #7f8c8d;
            }

            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }

            .stat-card {
                background: white;
                border-radius: 12px;
                padding: 20px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                display: flex;
                align-items: center;
                gap: 15px;
                transition: transform 0.2s, box-shadow 0.2s;
            }

            .stat-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
            }

            .stat-icon {
                width: 60px;
                height: 60px;
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 28px;
                color: white;
            }

            .stat-users .stat-icon { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
            .stat-students .stat-icon { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
            .stat-capsules .stat-icon { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
            .stat-quizzes .stat-icon { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }
            .stat-completion .stat-icon { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }
            .stat-quiz-score .stat-icon { background: linear-gradient(135deg, #30cfd0 0%, #330867 100%); }

            .stat-content h3 {
                margin: 0;
                font-size: 32px;
                color: #2c3e50;
                font-weight: 700;
            }

            .stat-content p {
                margin: 5px 0 0 0;
                color: #7f8c8d;
                font-size: 14px;
            }

            .charts-section {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }

            .chart-container {
                background: white;
                border-radius: 12px;
                padding: 20px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            }

            .chart-container.full-width {
                grid-column: 1 / -1;
            }

            .chart-container h2 {
                margin: 0 0 20px 0;
                color: #2c3e50;
                font-size: 18px;
            }

            .users-section, .activity-section {
                background: white;
                border-radius: 12px;
                padding: 20px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                margin-bottom: 20px;
            }

            .section-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
            }

            .section-header h2 {
                margin: 0;
                color: #2c3e50;
            }

            .search-box {
                position: relative;
                display: flex;
                align-items: center;
            }

            .search-box i {
                position: absolute;
                left: 12px;
                color: #7f8c8d;
            }

            .search-box input {
                padding: 10px 10px 10px 38px;
                border: 2px solid #ecf0f1;
                border-radius: 8px;
                font-size: 14px;
                width: 250px;
                transition: border-color 0.3s;
            }

            .search-box input:focus {
                outline: none;
                border-color: #3498db;
            }

            .table-container {
                overflow-x: auto;
            }

            .users-table {
                width: 100%;
                border-collapse: collapse;
            }

            .users-table th {
                background: #f8f9fa;
                padding: 12px;
                text-align: left;
                font-weight: 600;
                color: #2c3e50;
                border-bottom: 2px solid #ecf0f1;
            }

            .users-table td {
                padding: 12px;
                border-bottom: 1px solid #ecf0f1;
            }

            .users-table tbody tr:hover {
                background: #f8f9fa;
            }

            .badge {
                padding: 4px 10px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 600;
            }

            .badge-admin {
                background: #e74c3c;
                color: white;
            }

            .badge-student {
                background: #3498db;
                color: white;
            }

            .badge-active {
                background: #2ecc71;
                color: white;
            }

            .badge-inactive {
                background: #95a5a6;
                color: white;
            }

            .activity-list {
                max-height: 400px;
                overflow-y: auto;
            }

            .activity-item {
                padding: 15px;
                border-bottom: 1px solid #ecf0f1;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .activity-item:last-child {
                border-bottom: none;
            }

            .activity-info {
                flex: 1;
            }

            .activity-info strong {
                color: #2c3e50;
            }

            .activity-score {
                font-weight: 600;
                padding: 6px 12px;
                border-radius: 8px;
            }

            .activity-score.passed {
                background: #d5f4e6;
                color: #27ae60;
            }

            .activity-score.failed {
                background: #fadbd8;
                color: #e74c3c;
            }

            .btn {
                padding: 10px 20px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 14px;
                font-weight: 600;
                transition: all 0.3s;
                display: inline-flex;
                align-items: center;
                gap: 8px;
            }

            .btn-primary {
                background: #3498db;
                color: white;
            }

            .btn-primary:hover {
                background: #2980b9;
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
            }
        </style>
    `;

    // Load dashboard data
    loadDashboardData();

    // Event listeners
    container.querySelector('#refreshBtn').addEventListener('click', loadDashboardData);
    container.querySelector('#userSearch').addEventListener('input', filterUsers);

    return container;
}

let allUsersData = [];
let charts = {};

async function loadDashboardData() {
    const loadingIndicator = document.getElementById('loadingIndicator');
    const dashboardContent = document.getElementById('dashboardContent');

    if (loadingIndicator) loadingIndicator.style.display = 'block';
    if (dashboardContent) dashboardContent.style.display = 'none';

    try {
        // Fetch admin stats and users data
        const [statsResponse, usersResponse] = await Promise.all([
            fetch(`${API_BASE_URL}/dashboard/admin_stats/`, {
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                }
            }),
            fetch(`${API_BASE_URL}/dashboard/users/`, {
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
        ]);

        if (!statsResponse.ok || !usersResponse.ok) {
            throw new Error('Failed to fetch dashboard data');
        }

        const stats = await statsResponse.json();
        const usersData = await usersResponse.json();

        // Update statistics cards
        updateStatistics(stats);

        // Update charts
        updateCharts(stats);

        // Update users table
        allUsersData = usersData.users;
        updateUsersTable(usersData.users);

        // Update recent activity
        updateRecentActivity(stats.recent_quiz_attempts || []);

        if (loadingIndicator) loadingIndicator.style.display = 'none';
        if (dashboardContent) dashboardContent.style.display = 'block';

    } catch (error) {
        console.error('Error loading dashboard:', error);
        if (loadingIndicator) {
            loadingIndicator.innerHTML = `
                <div style="color: #e74c3c;">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Failed to load dashboard data. Please ensure you are logged in as an admin.</p>
                    <button onclick="window.location.reload()" class="btn btn-primary">Retry</button>
                </div>
            `;
        }
    }
}

function updateStatistics(stats) {
    document.getElementById('totalUsers').textContent = stats.total_users || 0;
    document.getElementById('totalStudents').textContent = stats.total_students || 0;
    document.getElementById('totalCapsules').textContent = stats.total_capsules || 0;
    document.getElementById('totalQuizzes').textContent = stats.total_quizzes || 0;
    document.getElementById('avgCompletion').textContent = (stats.average_completion_rate || 0).toFixed(1) + '%';
    document.getElementById('avgQuizScore').textContent = (stats.average_quiz_score || 0).toFixed(1) + '%';
}

function updateCharts(stats) {
    // Wait for Chart.js to load
    const initCharts = () => {
        if (!window.Chart) {
            setTimeout(initCharts, 100);
            return;
        }

        // Subject Distribution Chart
        const subjectCtx = document.getElementById('subjectChart');
        if (subjectCtx) {
            if (charts.subject) charts.subject.destroy();
            charts.subject = new Chart(subjectCtx, {
                type: 'doughnut',
                data: {
                    labels: stats.subject_distribution.map(s => s.name),
                    datasets: [{
                        data: stats.subject_distribution.map(s => s.capsule_count),
                        backgroundColor: [
                            '#3498db', '#e74c3c', '#2ecc71', '#f39c12',
                            '#9b59b6', '#1abc9c', '#34495e', '#e67e22'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        }

        // Grade Distribution Chart
        const gradeCtx = document.getElementById('gradeChart');
        if (gradeCtx) {
            if (charts.grade) charts.grade.destroy();
            charts.grade = new Chart(gradeCtx, {
                type: 'bar',
                data: {
                    labels: stats.grade_distribution.map(g => g.name),
                    datasets: [{
                        label: 'Capsules per Grade',
                        data: stats.grade_distribution.map(g => g.capsule_count),
                        backgroundColor: '#3498db'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }

        // User Engagement Chart
        const engagementCtx = document.getElementById('engagementChart');
        if (engagementCtx) {
            if (charts.engagement) charts.engagement.destroy();
            charts.engagement = new Chart(engagementCtx, {
                type: 'line',
                data: {
                    labels: ['Total Users', 'Students', 'Capsules', 'Quizzes', 'Completed', 'Attempts'],
                    datasets: [{
                        label: 'Platform Activity',
                        data: [
                            stats.total_users,
                            stats.total_students,
                            stats.total_capsules,
                            stats.total_quizzes,
                            stats.completed_capsules,
                            stats.total_quiz_attempts
                        ],
                        borderColor: '#3498db',
                        backgroundColor: 'rgba(52, 152, 219, 0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
    };

    initCharts();
}

function updateUsersTable(users) {
    const tbody = document.getElementById('usersTableBody');
    if (!tbody) return;

    if (users.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" style="text-align: center;">No users found</td></tr>';
        return;
    }

    tbody.innerHTML = users.map(user => `
        <tr>
            <td><strong>${user.username}</strong></td>
            <td>${user.email || 'N/A'}</td>
            <td><span class="badge ${user.is_staff ? 'badge-admin' : 'badge-student'}">${user.is_staff ? 'Admin' : 'Student'}</span></td>
            <td>${new Date(user.date_joined).toLocaleDateString()}</td>
            <td>${user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'}</td>
            <td>${user.capsules_completed || 0} / ${user.capsules_started || 0}</td>
            <td>${user.quizzes_passed || 0} / ${user.quizzes_taken || 0}</td>
            <td>${user.avg_score ? user.avg_score.toFixed(1) + '%' : 'N/A'}</td>
            <td><span class="badge ${user.is_active ? 'badge-active' : 'badge-inactive'}">${user.is_active ? 'Active' : 'Inactive'}</span></td>
        </tr>
    `).join('');
}

function updateRecentActivity(attempts) {
    const activityContainer = document.getElementById('recentActivity');
    if (!activityContainer) return;

    if (attempts.length === 0) {
        activityContainer.innerHTML = '<p style="color: #7f8c8d; text-align: center;">No recent activity</p>';
        return;
    }

    activityContainer.innerHTML = attempts.map(attempt => `
        <div class="activity-item">
            <div class="activity-info">
                <strong>${attempt.learner__username}</strong> completed 
                <span style="color: #3498db;">${attempt.quiz__title}</span>
                <br>
                <small style="color: #7f8c8d;">${new Date(attempt.completed_at).toLocaleString()}</small>
            </div>
            <div class="activity-score ${attempt.passed ? 'passed' : 'failed'}">
                ${attempt.score} / ${attempt.max_score}
                ${attempt.passed ? '✓' : '✗'}
            </div>
        </div>
    `).join('');
}

function filterUsers() {
    const searchTerm = document.getElementById('userSearch').value.toLowerCase();
    const filteredUsers = allUsersData.filter(user => 
        user.username.toLowerCase().includes(searchTerm) ||
        (user.email && user.email.toLowerCase().includes(searchTerm))
    );
    updateUsersTable(filteredUsers);
}
