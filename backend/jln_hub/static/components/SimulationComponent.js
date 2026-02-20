/**
 * Learning Simulation Component
 * 
 * Provides interactive simulations for science and math concepts.
 * Supports various simulation types with AI-generated hints.
 */
import { apiClient } from '../utils/api.js';

export class SimulationComponent {
    constructor(container, simulation) {
        this.container = container;
        this.simulation = simulation;
        this.interactionId = null;
        this.startTime = null;
        this.hintsViewed = 0;
        this.interactionData = {};
    }

    async render() {
        this.startTime = Date.now();
        
        this.container.innerHTML = `
            <div class="simulation-container" id="sim-${this.simulation.id}">
                <div class="simulation-header">
                    <h3>🔬 ${this.simulation.title}</h3>
                    <span class="sim-type-badge">${this.getTypeLabel(this.simulation.simulation_type)}</span>
                </div>
                
                <p class="simulation-description">${this.simulation.description}</p>
                
                ${this.simulation.learning_objectives?.length ? `
                    <div class="sim-objectives">
                        <h4>Learning Objectives:</h4>
                        <ul>
                            ${this.simulation.learning_objectives.map(obj => `<li>${obj}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                <div class="simulation-instructions">
                    <p><strong>Instructions:</strong> ${this.simulation.instructions || 'Explore the simulation below.'}</p>
                </div>
                
                <div class="simulation-canvas" id="sim-canvas-${this.simulation.id}">
                    ${this.renderSimulation()}
                </div>
                
                <div class="simulation-controls">
                    <button class="btn btn-hint" id="hint-btn-${this.simulation.id}">
                        💡 Get Hint (${this.simulation.hints?.length || 0} available)
                    </button>
                    <button class="btn btn-reset" id="reset-btn-${this.simulation.id}">
                        🔄 Reset
                    </button>
                    <button class="btn btn-primary" id="complete-btn-${this.simulation.id}">
                        ✓ Mark Complete
                    </button>
                </div>
                
                <div class="hint-display" id="hint-display-${this.simulation.id}" style="display: none;">
                </div>
                
                <div class="simulation-feedback" id="feedback-${this.simulation.id}" style="display: none;">
                </div>
            </div>
        `;

        this.attachEventListeners();
        await this.startSimulation();
    }

    getTypeLabel(type) {
        const labels = {
            'math_visualization': 'Math Visualization',
            'science_experiment': 'Science Experiment',
            'interactive_diagram': 'Interactive Diagram',
            'step_by_step': 'Step by Step'
        };
        return labels[type] || type;
    }

    renderSimulation() {
        const config = this.simulation.config || {};
        const type = this.simulation.simulation_type;

        switch (type) {
            case 'math_visualization':
                return this.renderMathVisualization(config);
            case 'science_experiment':
                return this.renderScienceExperiment(config);
            case 'interactive_diagram':
                return this.renderInteractiveDiagram(config);
            case 'step_by_step':
                return this.renderStepByStep(config);
            default:
                return this.renderGenericSimulation(config);
        }
    }

    renderMathVisualization(config) {
        if (config.type === 'fraction') {
            return this.renderFractionVisualizer(config);
        } else if (config.type === 'array') {
            return this.renderMultiplicationArrays(config);
        }
        return this.renderGenericMath(config);
    }

    renderFractionVisualizer(config) {
        const initial = config.initial_values || { numerator: 1, denominator: 2 };
        return `
            <div class="fraction-visualizer">
                <div class="fraction-controls">
                    <div class="slider-group">
                        <label>Numerator: <span id="num-value-${this.simulation.id}">${initial.numerator}</span></label>
                        <input type="range" id="numerator-${this.simulation.id}" 
                               min="0" max="12" value="${initial.numerator}" class="fraction-slider">
                    </div>
                    <div class="slider-group">
                        <label>Denominator: <span id="den-value-${this.simulation.id}">${initial.denominator}</span></label>
                        <input type="range" id="denominator-${this.simulation.id}" 
                               min="1" max="12" value="${initial.denominator}" class="fraction-slider">
                    </div>
                </div>
                <div class="fraction-display">
                    <div class="fraction-number">
                        <span class="numerator" id="frac-num-${this.simulation.id}">${initial.numerator}</span>
                        <hr>
                        <span class="denominator" id="frac-den-${this.simulation.id}">${initial.denominator}</span>
                    </div>
                    <span class="equals">=</span>
                    <span class="decimal" id="decimal-${this.simulation.id}">${(initial.numerator / initial.denominator).toFixed(2)}</span>
                </div>
                <div class="pie-chart-container">
                    <svg id="pie-chart-${this.simulation.id}" width="200" height="200" viewBox="0 0 200 200">
                        ${this.generatePieChart(initial.numerator, initial.denominator)}
                    </svg>
                </div>
                <div class="bar-model" id="bar-model-${this.simulation.id}">
                    ${this.generateBarModel(initial.numerator, initial.denominator)}
                </div>
            </div>
        `;
    }

    generatePieChart(numerator, denominator) {
        const slices = [];
        const anglePerSlice = 360 / denominator;
        
        for (let i = 0; i < denominator; i++) {
            const startAngle = i * anglePerSlice - 90;
            const endAngle = (i + 1) * anglePerSlice - 90;
            const filled = i < numerator;
            
            const x1 = 100 + 80 * Math.cos(startAngle * Math.PI / 180);
            const y1 = 100 + 80 * Math.sin(startAngle * Math.PI / 180);
            const x2 = 100 + 80 * Math.cos(endAngle * Math.PI / 180);
            const y2 = 100 + 80 * Math.sin(endAngle * Math.PI / 180);
            
            const largeArc = anglePerSlice > 180 ? 1 : 0;
            
            slices.push(`
                <path d="M 100 100 L ${x1} ${y1} A 80 80 0 ${largeArc} 1 ${x2} ${y2} Z"
                      fill="${filled ? '#4CAF50' : '#e0e0e0'}"
                      stroke="#333" stroke-width="2"/>
            `);
        }
        
        return slices.join('');
    }

    generateBarModel(numerator, denominator) {
        const bars = [];
        for (let i = 0; i < denominator; i++) {
            const filled = i < numerator;
            bars.push(`<div class="bar-segment ${filled ? 'filled' : ''}"></div>`);
        }
        return bars.join('');
    }

    renderMultiplicationArrays(config) {
        const maxRows = config.max_rows || 10;
        const maxCols = config.max_columns || 10;
        return `
            <div class="array-visualizer">
                <div class="array-controls">
                    <div class="slider-group">
                        <label>Rows: <span id="rows-value-${this.simulation.id}">3</span></label>
                        <input type="range" id="rows-${this.simulation.id}" 
                               min="1" max="${maxRows}" value="3" class="array-slider">
                    </div>
                    <div class="slider-group">
                        <label>Columns: <span id="cols-value-${this.simulation.id}">4</span></label>
                        <input type="range" id="cols-${this.simulation.id}" 
                               min="1" max="${maxCols}" value="4" class="array-slider">
                    </div>
                </div>
                <div class="array-equation" id="array-equation-${this.simulation.id}">
                    3 × 4 = 12
                </div>
                <div class="array-grid" id="array-grid-${this.simulation.id}">
                    ${this.generateArrayGrid(3, 4)}
                </div>
            </div>
        `;
    }

    generateArrayGrid(rows, cols) {
        let grid = '';
        for (let r = 0; r < rows; r++) {
            grid += '<div class="array-row">';
            for (let c = 0; c < cols; c++) {
                grid += '<div class="array-dot"></div>';
            }
            grid += '</div>';
        }
        return grid;
    }

    renderGenericMath(config) {
        return `
            <div class="generic-math">
                <p>Interactive math visualization</p>
                <div class="math-canvas" id="math-canvas-${this.simulation.id}"></div>
            </div>
        `;
    }

    renderScienceExperiment(config) {
        if (config.type === 'cycle_diagram') {
            return this.renderCycleDiagram(config);
        } else if (config.type === 'growth_simulation') {
            return this.renderGrowthSimulation(config);
        }
        return this.renderGenericExperiment(config);
    }

    renderCycleDiagram(config) {
        const stages = config.stages || ['stage1', 'stage2', 'stage3', 'stage4'];
        return `
            <div class="cycle-diagram">
                <svg viewBox="0 0 400 400" width="400" height="400">
                    <!-- Arrows -->
                    <path d="M 200 50 Q 350 50 350 200" fill="none" stroke="#2196F3" stroke-width="3" marker-end="url(#arrow)"/>
                    <path d="M 350 200 Q 350 350 200 350" fill="none" stroke="#2196F3" stroke-width="3" marker-end="url(#arrow)"/>
                    <path d="M 200 350 Q 50 350 50 200" fill="none" stroke="#2196F3" stroke-width="3" marker-end="url(#arrow)"/>
                    <path d="M 50 200 Q 50 50 200 50" fill="none" stroke="#2196F3" stroke-width="3" marker-end="url(#arrow)"/>
                    
                    <defs>
                        <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
                            <path d="M0,0 L0,6 L9,3 z" fill="#2196F3"/>
                        </marker>
                    </defs>
                    
                    ${stages.map((stage, i) => {
                        const positions = [
                            { x: 200, y: 30 },
                            { x: 370, y: 200 },
                            { x: 200, y: 370 },
                            { x: 30, y: 200 }
                        ];
                        const pos = positions[i % 4];
                        return `
                            <g class="cycle-stage" data-stage="${stage}" style="cursor: pointer;">
                                <circle cx="${pos.x}" cy="${pos.y}" r="40" fill="#4CAF50" stroke="#333" stroke-width="2"/>
                                <text x="${pos.x}" y="${pos.y}" text-anchor="middle" dy="5" fill="white" font-size="10">
                                    ${stage.replace('_', ' ')}
                                </text>
                            </g>
                        `;
                    }).join('')}
                </svg>
                <div class="stage-info" id="stage-info-${this.simulation.id}">
                    <p>Click on a stage to learn more about it.</p>
                </div>
            </div>
        `;
    }

    renderGrowthSimulation(config) {
        return `
            <div class="growth-simulation">
                <div class="growth-controls">
                    <div class="variable-control">
                        <label>💧 Water Level:</label>
                        <input type="range" id="water-${this.simulation.id}" min="0" max="100" value="50">
                        <span id="water-value-${this.simulation.id}">50%</span>
                    </div>
                    <div class="variable-control">
                        <label>☀️ Sunlight:</label>
                        <input type="range" id="sunlight-${this.simulation.id}" min="0" max="100" value="50">
                        <span id="sunlight-value-${this.simulation.id}">50%</span>
                    </div>
                </div>
                <div class="growth-display">
                    <div class="plant-container" id="plant-${this.simulation.id}">
                        <div class="soil"></div>
                        <div class="stem" style="height: 50px;"></div>
                        <div class="leaves">🌱</div>
                    </div>
                    <div class="growth-meter">
                        <label>Growth: <span id="growth-value-${this.simulation.id}">50%</span></label>
                        <div class="meter-bar">
                            <div class="meter-fill" id="meter-fill-${this.simulation.id}" style="width: 50%;"></div>
                        </div>
                    </div>
                </div>
                <button class="btn" id="grow-btn-${this.simulation.id}">⏩ Grow Plant</button>
            </div>
        `;
    }

    renderGenericExperiment(config) {
        return `
            <div class="generic-experiment">
                <p>Interactive science experiment</p>
                <div class="experiment-area" id="experiment-${this.simulation.id}"></div>
            </div>
        `;
    }

    renderInteractiveDiagram(config) {
        if (config.type === 'circuit_builder') {
            return this.renderCircuitBuilder(config);
        }
        return `
            <div class="interactive-diagram">
                <p>Interactive diagram - click elements to explore</p>
                <div class="diagram-area" id="diagram-${this.simulation.id}"></div>
            </div>
        `;
    }

    renderCircuitBuilder(config) {
        return `
            <div class="circuit-builder">
                <div class="component-palette">
                    <h4>Components:</h4>
                    <div class="component-btn" data-component="battery">🔋 Battery</div>
                    <div class="component-btn" data-component="bulb">💡 Bulb</div>
                    <div class="component-btn" data-component="switch">🔘 Switch</div>
                    <div class="component-btn" data-component="wire">➖ Wire</div>
                </div>
                <div class="circuit-area" id="circuit-${this.simulation.id}">
                    <p>Drag components here to build your circuit</p>
                </div>
                <div class="circuit-status" id="circuit-status-${this.simulation.id}">
                    Circuit Status: <span class="status-badge">Open</span>
                </div>
            </div>
        `;
    }

    renderStepByStep(config) {
        const steps = config.steps || ['Step 1', 'Step 2', 'Step 3'];
        return `
            <div class="step-by-step">
                <div class="steps-progress">
                    ${steps.map((step, i) => `
                        <div class="step-indicator ${i === 0 ? 'active' : ''}" data-step="${i}">
                            ${i + 1}
                        </div>
                    `).join('')}
                </div>
                <div class="step-content" id="step-content-${this.simulation.id}">
                    <h4>${steps[0]}</h4>
                    <p>Follow the steps to complete this activity.</p>
                </div>
                <div class="step-navigation">
                    <button class="btn" id="prev-step-${this.simulation.id}" disabled>← Previous</button>
                    <button class="btn btn-primary" id="next-step-${this.simulation.id}">Next →</button>
                </div>
            </div>
        `;
    }

    renderGenericSimulation(config) {
        return `
            <div class="generic-simulation">
                <p>Interactive simulation area</p>
                <div class="sim-area" id="generic-sim-${this.simulation.id}">
                    <p>Explore and interact with this simulation.</p>
                </div>
            </div>
        `;
    }

    attachEventListeners() {
        // Hint button
        const hintBtn = document.getElementById(`hint-btn-${this.simulation.id}`);
        if (hintBtn) {
            hintBtn.addEventListener('click', () => this.showHint());
        }

        // Reset button
        const resetBtn = document.getElementById(`reset-btn-${this.simulation.id}`);
        if (resetBtn) {
            resetBtn.addEventListener('click', () => this.resetSimulation());
        }

        // Complete button
        const completeBtn = document.getElementById(`complete-btn-${this.simulation.id}`);
        if (completeBtn) {
            completeBtn.addEventListener('click', () => this.completeSimulation());
        }

        // Type-specific listeners
        this.attachTypeSpecificListeners();
    }

    attachTypeSpecificListeners() {
        const type = this.simulation.simulation_type;
        const config = this.simulation.config || {};

        if (type === 'math_visualization') {
            if (config.type === 'fraction') {
                this.attachFractionListeners();
            } else if (config.type === 'array') {
                this.attachArrayListeners();
            }
        } else if (type === 'science_experiment') {
            if (config.type === 'growth_simulation') {
                this.attachGrowthListeners();
            }
        }
    }

    attachFractionListeners() {
        const numSlider = document.getElementById(`numerator-${this.simulation.id}`);
        const denSlider = document.getElementById(`denominator-${this.simulation.id}`);

        if (numSlider && denSlider) {
            const updateFraction = () => {
                const num = parseInt(numSlider.value);
                const den = parseInt(denSlider.value);

                document.getElementById(`num-value-${this.simulation.id}`).textContent = num;
                document.getElementById(`den-value-${this.simulation.id}`).textContent = den;
                document.getElementById(`frac-num-${this.simulation.id}`).textContent = num;
                document.getElementById(`frac-den-${this.simulation.id}`).textContent = den;
                document.getElementById(`decimal-${this.simulation.id}`).textContent = (num / den).toFixed(2);

                // Update pie chart
                const pieChart = document.getElementById(`pie-chart-${this.simulation.id}`);
                if (pieChart) {
                    pieChart.innerHTML = this.generatePieChart(num, den);
                }

                // Update bar model
                const barModel = document.getElementById(`bar-model-${this.simulation.id}`);
                if (barModel) {
                    barModel.innerHTML = this.generateBarModel(num, den);
                }

                this.interactionData.fraction_changes = (this.interactionData.fraction_changes || 0) + 1;
            };

            numSlider.addEventListener('input', updateFraction);
            denSlider.addEventListener('input', updateFraction);
        }
    }

    attachArrayListeners() {
        const rowsSlider = document.getElementById(`rows-${this.simulation.id}`);
        const colsSlider = document.getElementById(`cols-${this.simulation.id}`);

        if (rowsSlider && colsSlider) {
            const updateArray = () => {
                const rows = parseInt(rowsSlider.value);
                const cols = parseInt(colsSlider.value);

                document.getElementById(`rows-value-${this.simulation.id}`).textContent = rows;
                document.getElementById(`cols-value-${this.simulation.id}`).textContent = cols;
                document.getElementById(`array-equation-${this.simulation.id}`).textContent = 
                    `${rows} × ${cols} = ${rows * cols}`;

                const grid = document.getElementById(`array-grid-${this.simulation.id}`);
                if (grid) {
                    grid.innerHTML = this.generateArrayGrid(rows, cols);
                }

                this.interactionData.array_changes = (this.interactionData.array_changes || 0) + 1;
            };

            rowsSlider.addEventListener('input', updateArray);
            colsSlider.addEventListener('input', updateArray);
        }
    }

    attachGrowthListeners() {
        const waterSlider = document.getElementById(`water-${this.simulation.id}`);
        const sunSlider = document.getElementById(`sunlight-${this.simulation.id}`);
        const growBtn = document.getElementById(`grow-btn-${this.simulation.id}`);

        const updateGrowth = () => {
            const water = parseInt(waterSlider?.value || 50);
            const sun = parseInt(sunSlider?.value || 50);
            
            if (waterSlider) {
                document.getElementById(`water-value-${this.simulation.id}`).textContent = `${water}%`;
            }
            if (sunSlider) {
                document.getElementById(`sunlight-value-${this.simulation.id}`).textContent = `${sun}%`;
            }

            // Calculate optimal growth (best around 50-70 for both)
            const waterScore = water >= 40 && water <= 70 ? 1 : 0.5;
            const sunScore = sun >= 50 && sun <= 80 ? 1 : 0.5;
            const growth = Math.round((waterScore + sunScore) / 2 * 100);

            document.getElementById(`growth-value-${this.simulation.id}`).textContent = `${growth}%`;
            document.getElementById(`meter-fill-${this.simulation.id}`).style.width = `${growth}%`;
        };

        if (waterSlider) waterSlider.addEventListener('input', updateGrowth);
        if (sunSlider) sunSlider.addEventListener('input', updateGrowth);

        if (growBtn) {
            growBtn.addEventListener('click', () => {
                const plant = document.querySelector(`#plant-${this.simulation.id} .leaves`);
                const stem = document.querySelector(`#plant-${this.simulation.id} .stem`);
                
                if (plant && stem) {
                    const currentHeight = parseInt(stem.style.height) || 50;
                    stem.style.height = `${Math.min(currentHeight + 20, 150)}px`;
                    
                    if (currentHeight >= 100) {
                        plant.textContent = '🌿';
                    }
                    if (currentHeight >= 130) {
                        plant.textContent = '🌻';
                    }
                }
                
                this.interactionData.grow_clicks = (this.interactionData.grow_clicks || 0) + 1;
            });
        }
    }

    async startSimulation() {
        try {
            const result = await apiClient.post(`/simulations/${this.simulation.id}/start/`, {});
            if (result && result.interaction_id) {
                this.interactionId = result.interaction_id;
            }
        } catch (error) {
            console.log('Note: Simulation tracking requires authentication');
        }
    }

    async showHint() {
        const hints = this.simulation.hints || [];
        const hintDisplay = document.getElementById(`hint-display-${this.simulation.id}`);
        
        if (this.hintsViewed < hints.length && hintDisplay) {
            hintDisplay.style.display = 'block';
            hintDisplay.innerHTML = `
                <div class="hint-box">
                    <strong>💡 Hint ${this.hintsViewed + 1}:</strong>
                    <p>${hints[this.hintsViewed]}</p>
                </div>
            `;
            this.hintsViewed++;
            
            const hintBtn = document.getElementById(`hint-btn-${this.simulation.id}`);
            if (hintBtn) {
                const remaining = hints.length - this.hintsViewed;
                hintBtn.textContent = `💡 Get Hint (${remaining} remaining)`;
                if (remaining === 0) {
                    hintBtn.disabled = true;
                }
            }
        }
    }

    resetSimulation() {
        this.hintsViewed = 0;
        this.interactionData = {};
        this.render();
    }

    async completeSimulation() {
        const timeSpent = Math.round((Date.now() - this.startTime) / 1000);
        
        const feedbackDiv = document.getElementById(`feedback-${this.simulation.id}`);
        if (feedbackDiv) {
            feedbackDiv.style.display = 'block';
            feedbackDiv.innerHTML = `
                <div class="completion-feedback success">
                    <h4>✓ Simulation Completed!</h4>
                    <p>Time spent: ${Math.floor(timeSpent / 60)}m ${timeSpent % 60}s</p>
                    <p>Hints used: ${this.hintsViewed}</p>
                </div>
            `;
        }

        // Record completion
        if (this.interactionId) {
            try {
                await apiClient.post(`/simulations/${this.simulation.id}/complete/`, {
                    interaction_id: this.interactionId,
                    time_spent: timeSpent,
                    interaction_data: this.interactionData,
                    hints_used: this.hintsViewed,
                    completed_successfully: true
                });
            } catch (error) {
                console.log('Note: Completion tracking requires authentication');
            }
        }
    }
}
