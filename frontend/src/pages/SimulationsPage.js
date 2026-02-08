/**
 * Simulations Page
 * 
 * Displays available learning simulations for science and math concepts.
 * Allows filtering by subject, grade, and simulation type.
 */
import { apiClient } from '../utils/api.js';
import { SimulationComponent } from '../components/SimulationComponent.js';

export class SimulationsPage {
    constructor(container) {
        this.container = container;
        this.simulations = [];
        this.filters = {
            subject: '',
            grade: '',
            type: ''
        };
    }

    async render() {
        this.container.innerHTML = `
            <div class="simulations-page">
                <header class="page-header">
                    <h1>🔬 Learning Simulations</h1>
                    <p>Explore interactive simulations for science and mathematics concepts</p>
                </header>

                <div class="simulation-filters">
                    <select id="sim-subject-filter" class="filter-select">
                        <option value="">All Subjects</option>
                    </select>
                    <select id="sim-grade-filter" class="filter-select">
                        <option value="">All Grades</option>
                    </select>
                    <select id="sim-type-filter" class="filter-select">
                        <option value="">All Types</option>
                        <option value="math_visualization">Math Visualization</option>
                        <option value="science_experiment">Science Experiment</option>
                        <option value="interactive_diagram">Interactive Diagram</option>
                        <option value="step_by_step">Step by Step</option>
                    </select>
                </div>

                <div id="simulations-grid" class="simulations-grid">
                    <p class="loading">Loading simulations...</p>
                </div>

                <div id="simulation-viewer" class="simulation-viewer" style="display: none;">
                    <button id="close-simulation" class="btn btn-back">← Back to Simulations</button>
                    <div id="simulation-container"></div>
                </div>
            </div>
        `;

        await this.loadFilters();
        await this.loadSimulations();
        this.attachEventListeners();
    }

    async loadFilters() {
        try {
            const [subjectsResponse, gradesResponse] = await Promise.all([
                apiClient.get('/subjects/'),
                apiClient.get('/grades/')
            ]);

            // Handle paginated responses (results array) or direct arrays
            const subjects = Array.isArray(subjectsResponse) ? subjectsResponse : (subjectsResponse?.results || []);
            const grades = Array.isArray(gradesResponse) ? gradesResponse : (gradesResponse?.results || []);

            const subjectSelect = document.getElementById('sim-subject-filter');
            const gradeSelect = document.getElementById('sim-grade-filter');

            if (subjects.length && subjectSelect) {
                subjects.forEach(subject => {
                    subjectSelect.innerHTML += `<option value="${subject.id}">${subject.name}</option>`;
                });
            }

            if (grades.length && gradeSelect) {
                grades.forEach(grade => {
                    gradeSelect.innerHTML += `<option value="${grade.id}">${grade.name}</option>`;
                });
            }
        } catch (error) {
            console.error('Failed to load filters:', error);
        }
    }

    async loadSimulations() {
        const grid = document.getElementById('simulations-grid');
        
        try {
            let url = '/simulations/';
            const params = new URLSearchParams();
            
            if (this.filters.subject) params.append('subject', this.filters.subject);
            if (this.filters.grade) params.append('grade', this.filters.grade);
            if (this.filters.type) params.append('type', this.filters.type);
            
            const queryString = params.toString();
            if (queryString) url += `?${queryString}`;

            const response = await apiClient.get(url);
            // Handle paginated response or direct array
            this.simulations = Array.isArray(response) ? response : (response?.results || []);
            this.displaySimulations();
        } catch (error) {
            grid.innerHTML = `
                <div class="error-message">
                    <p>Unable to load simulations. Please try again later.</p>
                </div>
            `;
        }
    }

    displaySimulations() {
        const grid = document.getElementById('simulations-grid');

        if (!this.simulations.length) {
            grid.innerHTML = `
                <div class="no-simulations">
                    <p>No simulations available yet.</p>
                    <p class="text-muted">Check back soon for interactive learning experiences!</p>
                </div>
            `;
            return;
        }

        grid.innerHTML = this.simulations.map(sim => `
            <div class="simulation-card" data-sim-id="${sim.id}">
                <div class="sim-card-header">
                    <span class="sim-type-icon">${this.getTypeIcon(sim.simulation_type)}</span>
                    <span class="sim-difficulty ${sim.difficulty_level}">${sim.difficulty_level}</span>
                </div>
                <h3 class="sim-title">${sim.title}</h3>
                <p class="sim-description">${sim.description.substring(0, 100)}${sim.description.length > 100 ? '...' : ''}</p>
                <div class="sim-meta">
                    <span>${sim.subject_name}</span>
                    <span>${sim.grade_name}</span>
                    <span>⏱️ ${sim.estimated_time} min</span>
                </div>
                <button class="btn btn-primary start-simulation" data-sim-id="${sim.id}">
                    Start Simulation
                </button>
            </div>
        `).join('');
    }

    getTypeIcon(type) {
        const icons = {
            'math_visualization': '📐',
            'science_experiment': '🧪',
            'interactive_diagram': '📊',
            'step_by_step': '📝'
        };
        return icons[type] || '🔬';
    }

    attachEventListeners() {
        // Filter change handlers
        document.getElementById('sim-subject-filter')?.addEventListener('change', (e) => {
            this.filters.subject = e.target.value;
            this.loadSimulations();
        });

        document.getElementById('sim-grade-filter')?.addEventListener('change', (e) => {
            this.filters.grade = e.target.value;
            this.loadSimulations();
        });

        document.getElementById('sim-type-filter')?.addEventListener('change', (e) => {
            this.filters.type = e.target.value;
            this.loadSimulations();
        });

        // Start simulation
        this.container.addEventListener('click', async (e) => {
            if (e.target.classList.contains('start-simulation')) {
                const simId = e.target.dataset.simId;
                await this.openSimulation(simId);
            }
        });

        // Close simulation
        document.getElementById('close-simulation')?.addEventListener('click', () => {
            this.closeSimulation();
        });
    }

    async openSimulation(simId) {
        const simulation = this.simulations.find(s => s.id === parseInt(simId));
        
        if (!simulation) {
            // Fetch full details
            try {
                const fullSim = await apiClient.get(`/simulations/${simId}/`);
                if (fullSim) {
                    this.renderSimulationViewer(fullSim);
                }
            } catch (error) {
                console.error('Failed to load simulation:', error);
            }
        } else {
            // Get full details for config
            try {
                const fullSim = await apiClient.get(`/simulations/${simId}/`);
                this.renderSimulationViewer(fullSim);
            } catch (error) {
                console.error('Failed to load simulation details:', error);
            }
        }
    }

    renderSimulationViewer(simulation) {
        const grid = document.getElementById('simulations-grid');
        const viewer = document.getElementById('simulation-viewer');
        const container = document.getElementById('simulation-container');

        grid.style.display = 'none';
        viewer.style.display = 'block';

        const simComponent = new SimulationComponent(container, simulation);
        simComponent.render();
    }

    closeSimulation() {
        const grid = document.getElementById('simulations-grid');
        const viewer = document.getElementById('simulation-viewer');
        const container = document.getElementById('simulation-container');

        viewer.style.display = 'none';
        grid.style.display = 'grid';
        container.innerHTML = '';
    }
}
