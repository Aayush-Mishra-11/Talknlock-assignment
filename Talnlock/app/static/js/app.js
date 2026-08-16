document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const simulatorForm = document.getElementById('simulator-form');
    const adSpendInput = document.getElementById('ad_spend');
    const adSpendVal = document.getElementById('ad_spend_val');
    const btnSimulate = document.getElementById('btn-simulate');
    
    const resultsPlaceholder = document.getElementById('results-placeholder');
    const resultsActive = document.getElementById('results-active');
    const scoreNumber = document.getElementById('score-number');
    const scoreRing = document.getElementById('score-ring');
    const scoreRatingText = document.getElementById('score-rating-text');
    const baseValueText = document.getElementById('base-value-text');
    const shapContainer = document.getElementById('shap-factors-container');
    
    const btnRecommend = document.getElementById('btn-recommend');
    const recommendationsContainer = document.getElementById('recommendations-container');
    
    // Track current prediction industry for recommendations
    let currentIndustry = document.getElementById('industry').value;
    
    // Update industry tracker when changed
    document.getElementById('industry').addEventListener('change', (e) => {
        currentIndustry = e.target.value;
    });

    // Update Ad Spend display on slider change
    adSpendInput.addEventListener('input', (e) => {
        adSpendVal.textContent = e.target.value;
    });

    // Simple markdown-to-HTML formatter for LLM briefs
    function formatMarkdown(text) {
        if (!text) return "";
        let html = text;
        
        // Headers (e.g., ### Title)
        html = html.replace(/### (.*?)\n/g, '<h3>$1</h3>');
        html = html.replace(/#### (.*?)\n/g, '<h4>$1</h4>');
        
        // Bold (e.g., **text**)
        html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Bullet points (e.g., * list item)
        // Group list items into <ul> blocks
        html = html.replace(/^\s*\*\s+(.*?)$/gm, '<li>$1</li>');
        // Wrap adjacent <li> lines in <ul>
        // We can do a simple replacement for groups of list items
        html = html.replace(/(<li>.*?<\/li>)+/g, '<ul>$&</ul>');
        
        // Linebreaks
        html = html.replace(/\n/g, '<br>');
        
        return html;
    }

    // SVG Ring Animation
    function animateScore(score) {
        const ringCircumference = 471; // 2 * pi * r = 2 * 3.14159 * 75
        const offset = ringCircumference - (ringCircumference * score / 100);
        
        scoreRing.style.strokeDashoffset = offset;
        
        // Count up animation
        let count = 0.0;
        const duration = 1000; // 1 second
        const interval = 20; // 20ms
        const step = score / (duration / interval);
        
        const counter = setInterval(() => {
            count += step;
            if (count >= score) {
                scoreNumber.textContent = score.toFixed(1);
                clearInterval(counter);
            } else {
                scoreNumber.textContent = count.toFixed(1);
            }
        }, interval);
        
        // Determine Rating Color & Text
        let rating = "Fair";
        let color = "#f59e0b"; // warning orange
        
        if (score >= 80) {
            rating = "Excellent";
            color = "#10b981"; // success green
        } else if (score >= 60) {
            rating = "Good";
            color = "#6366f1"; // primary indigo
        } else if (score < 40) {
            rating = "Underperforming";
            color = "#ef4444"; // danger red
        }
        
        scoreRing.style.stroke = color;
        scoreRatingText.textContent = rating;
        scoreRatingText.style.color = color;
    }

    // Render local SHAP explainability factors
    function renderShapFactors(factors) {
        shapContainer.innerHTML = '';
        
        // Find max impact magnitude to scale bars proportionally
        const maxImpact = Math.max(...factors.map(f => Math.abs(f.impact)), 1.0);
        
        factors.forEach(f => {
            const item = document.createElement('div');
            item.className = 'shap-item';
            
            // Format labels for presentation
            let labelText = f.factor;
            if (f.factor.includes('_')) {
                labelText = f.factor.replace('_', ' ');
            }
            
            // Calculate width percentage relative to max impact
            const pctWidth = Math.max(5, (Math.abs(f.impact) / maxImpact) * 100);
            const directionClass = f.direction; // 'positive' or 'negative'
            const sign = f.impact >= 0 ? '+' : '';
            
            item.innerHTML = `
                <div class="shap-label" title="${labelText}">${labelText}</div>
                <div class="shap-bar-container">
                    <div class="shap-bar ${directionClass}" style="width: ${pctWidth}%"></div>
                </div>
                <div class="shap-value ${directionClass}">${sign}${f.impact.toFixed(2)}</div>
            `;
            
            shapContainer.appendChild(item);
        });
    }

    // Handle Simulator Submission
    simulatorForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Set loading state
        btnSimulate.disabled = true;
        btnSimulate.innerHTML = `<svg class="spinner" width="16px" height="16px" viewBox="0 0 66 66" xmlns="http://www.w3.org/2000/svg"><circle class="path" fill="none" stroke-width="6" stroke-linecap="round" cx="33" cy="33" r="30"></circle></svg> Simulating...`;
        
        const payload = {
            Industry: document.getElementById('industry').value,
            Platform: document.getElementById('platform').value,
            Content_Type: document.getElementById('content_type').value,
            Content_Topic: document.getElementById('topic').value,
            Posting_Day: document.getElementById('posting_day').value,
            Posting_Time: document.getElementById('posting_time').value,
            Ad_Spend: parseFloat(adSpendInput.value)
        };
        
        try {
            const response = await fetch('/api/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            
            if (!response.ok) {
                throw new Error('Server returned an error');
            }
            
            const data = await response.json();
            
            // Update UI
            resultsPlaceholder.classList.add('hidden');
            resultsActive.classList.remove('hidden');
            
            baseValueText.textContent = data.base_value.toFixed(1);
            
            // Run animations
            renderShapFactors(data.top_factors);
            animateScore(data.predicted_score);
            
        } catch (error) {
            console.error('Error during simulation:', error);
            alert('Failed to execute simulation. Make sure the API is active and models are trained.');
        } finally {
            btnSimulate.disabled = false;
            btnSimulate.innerHTML = `<i class="fa-solid fa-bolt"></i> Run Predictive Simulation`;
        }
    });

    // Handle Recommendation Requests
    btnRecommend.addEventListener('click', async () => {
        // Set loading state
        btnRecommend.disabled = true;
        btnRecommend.innerHTML = `<svg class="spinner" width="16px" height="16px" viewBox="0 0 66 66" xmlns="http://www.w3.org/2000/svg"><circle class="path" fill="none" stroke-width="6" stroke-linecap="round" cx="33" cy="33" r="30"></circle></svg> Searching & Reasoning...`;
        
        recommendationsContainer.innerHTML = `
            <div class="empty-state py-5">
                <svg class="spinner" width="40px" height="40px" viewBox="0 0 66 66" xmlns="http://www.w3.org/2000/svg" style="margin-bottom:15px"><circle class="path" fill="none" stroke-width="6" stroke-linecap="round" cx="33" cy="33" r="30" stroke="#6366f1"></circle></svg>
                <h3>Querying Local Recommender Space</h3>
                <p>Scoring configurations and calling the LLM layer. This may take a moment if Ollama is starting up...</p>
            </div>
        `;
        
        try {
            const response = await fetch('/api/recommend', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ Industry: currentIndustry })
            });
            
            if (!response.ok) {
                throw new Error('Server returned error');
            }
            
            const data = await response.json();
            
            // Build recommendations cards
            let cardsHtml = '';
            data.recommendations.forEach(r => {
                // Determine rank visual class
                const rankClass = r.rank === 1 ? 'rank-1' : '';
                
                cardsHtml += `
                    <div class="rec-card ${rankClass}">
                        <div class="rec-header">
                            <span class="rec-rank">Option #${r.rank}</span>
                            <span class="rec-score">${r.predicted_score.toFixed(1)}</span>
                        </div>
                        <div class="rec-details">
                            <div class="rec-detail-item">
                                <span>Platform:</span>
                                <span>${r.attributes.Platform}</span>
                            </div>
                            <div class="rec-detail-item">
                                <span>Format:</span>
                                <span>${r.attributes.Content_Type}</span>
                            </div>
                            <div class="rec-detail-item">
                                <span>Topic:</span>
                                <span>${r.attributes.Content_Topic}</span>
                            </div>
                            <div class="rec-detail-item">
                                <span>Posting Time:</span>
                                <span>${r.attributes.Posting_Time.split(' ')[0]}</span>
                            </div>
                        </div>
                    </div>
                `;
            });
            
            // Format LLM brief
            const formattedBrief = formatMarkdown(data.brief);
            
            recommendationsContainer.innerHTML = `
                <div class="recommender-grid">
                    ${cardsHtml}
                </div>
                <div class="campaign-brief-box">
                    <h3><i class="fa-solid fa-sparkles"></i> AI Strategic Copywriter & Insight Brief</h3>
                    <div class="campaign-brief-text">
                        ${formattedBrief}
                    </div>
                </div>
            `;
            
        } catch (error) {
            console.error('Error fetching recommendations:', error);
            recommendationsContainer.innerHTML = `
                <div class="empty-state py-5">
                    <i class="fa-solid fa-triangle-exclamation placeholder-icon" style="color:var(--danger-color)"></i>
                    <h3>Optimization Failed</h3>
                    <p>Could not load recommendations. Check that the backend server is running and models are trained.</p>
                </div>
            `;
        } finally {
            btnRecommend.disabled = false;
            btnRecommend.innerHTML = `<i class="fa-solid fa-sparkles"></i> Generate AI Campaign Brief`;
        }
    });
});
