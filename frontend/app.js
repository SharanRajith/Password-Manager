const API_URL = '';

document.addEventListener('DOMContentLoaded', async () => {
    try {
        const res = await fetch(`${API_URL}/vault`);
        if (res.status === 400) {
            document.getElementById('setup-view').style.display = 'block';
        } else {
            document.getElementById('login-view').style.display = 'block';
        }
    } catch (e) {
        console.error("Backend not reachable", e);
    }
});

document.getElementById('btn-setup').addEventListener('click', async () => {
    const pw = document.getElementById('setup-password').value;
    if (!pw) return;
    
    try {
        const res = await fetch(`${API_URL}/setup`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({master_password: pw})
        });
        const data = await res.json();
        
        if (res.ok) {
            document.getElementById('setup-view').style.display = 'none';
            document.getElementById('auth-math').style.display = 'block';
            document.getElementById('auth-math-content').innerHTML = `
                <div class="edu-box" style="margin-top: 0">
                    <strong><i class="icon">📘</i> Beginner's Concept: Building the Lock</strong>
                    <p>We just found two extremely large random prime numbers (<strong>p</strong> and <strong>q</strong>).<br><br>We multiplied them together to get <strong>n</strong> (your public lock). We also calculated <strong>φ(n)</strong>, a special math trick that helps us forge your private key. Since these numbers are so huge, no supercomputer on Earth can figure out what <strong>p</strong> and <strong>q</strong> are just by looking at <strong>n</strong>!</p>
                </div>
                <div style="color:var(--text-primary); font-weight:600; margin-top:1rem;">Your Unique Math Variables:</div>
                <div class="mono" style="margin-top:0.5rem; color:var(--math-text);">
                    <div>p: ${truncate(data.math_params.p, 30)}</div>
                    <div>q: ${truncate(data.math_params.q, 30)}</div>
                    <div style="margin-top:0.5rem">n = p*q (Modulus)</div>
                    <div>φ(n) = (p-1)*(q-1) (Totient)</div>
                </div>
                <div style="margin-top:1rem"><button onclick="location.reload()" class="outline-btn w-full">Continue to Login</button></div>
            `;
        } else {
            alert(data.detail);
        }
    } catch (e) {
        console.error(e);
    }
});

document.getElementById('btn-login').addEventListener('click', async () => {
    const pw = document.getElementById('login-password').value;
    if (!pw) return;
    
    try {
        const res = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({master_password: pw})
        });
        const data = await res.json();
        
        if (res.ok) {
            document.getElementById('auth-container').style.display = 'none';
            document.getElementById('vault-container').style.display = 'block';
            
            document.getElementById('param-p').innerText = truncate(data.math_params.p);
            document.getElementById('param-q').innerText = truncate(data.math_params.q);
            document.getElementById('param-n').innerText = truncate(data.public_key[1]);
            document.getElementById('param-phi').innerText = truncate(data.math_params.phi);
            document.getElementById('param-e').innerText = data.public_key[0];
            
            loadVault();
            setTimeout(updateChart, 100); // Initialize chart after container is visible
        } else {
            alert(data.detail);
        }
    } catch (e) {
        console.error(e);
    }
});

document.getElementById('btn-reset')?.addEventListener('click', async () => {
    if (confirm("Are you sure? This will permanently delete your vault and all encrypted passwords. You will need to setup a new master password.")) {
        try {
            await fetch(`${API_URL}/reset`, { method: 'POST' });
            location.reload();
        } catch (e) {
            console.error(e);
        }
    }
});

document.getElementById('btn-logout').addEventListener('click', () => {
    location.reload();
});

document.getElementById('btn-generate').addEventListener('click', async () => {
    const len = document.getElementById('gen-len').value;
    const upper = document.getElementById('gen-upper').checked;
    const lower = document.getElementById('gen-lower').checked;
    const digits = document.getElementById('gen-digits').checked;
    const special = document.getElementById('gen-special').checked;
    
    try {
        const res = await fetch(`${API_URL}/generate`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                length: parseInt(len),
                use_upper: upper,
                use_lower: lower,
                use_digits: digits,
                use_special: special
            })
        });
        const data = await res.json();
        if (res.ok) {
            document.getElementById('gen-result').style.display = 'block';
            document.getElementById('gen-pw').innerText = data.password;
            document.getElementById('gen-entropy').innerText = data.entropy;
            document.getElementById('gen-strength').innerText = data.strength;
            
            document.getElementById('add-pw').value = data.password;
        } else {
            alert(data.detail);
        }
    } catch (e) {
        console.error(e);
    }
});

document.getElementById('btn-add').addEventListener('click', async () => {
    const site = document.getElementById('add-site').value;
    const user = document.getElementById('add-user').value;
    const pw = document.getElementById('add-pw').value;
    
    if (!site || !user || !pw) return;
    
    try {
        const res = await fetch(`${API_URL}/vault`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({site, username: user, password: pw})
        });
        const data = await res.json();
        if (res.ok) {
            document.getElementById('encrypt-demo').style.display = 'block';
            
            const pArray = JSON.parse(data.encrypted);
            document.getElementById('encrypt-math-text').innerText = 
                `c = m^e (mod n)\n\nResulting Ciphertext Array:\n[${pArray.slice(0, 5).join(', ')}${pArray.length > 5 ? ', ...' : ''}]`;
                
            document.getElementById('add-site').value = '';
            document.getElementById('add-user').value = '';
            document.getElementById('add-pw').value = '';
            
            loadVault();
        }
    } catch (e) {
        console.error(e);
    }
});

async function loadVault() {
    try {
        const res = await fetch(`${API_URL}/vault`);
        const data = await res.json();
        
        const list = document.getElementById('vault-list');
        list.innerHTML = '';
        
        if (data.entries) {
            data.entries.forEach(entry => {
                const item = document.createElement('div');
                item.className = 'vault-item';
                
                const cArray = JSON.parse(entry.encrypted_password);
                const shortCipher = `[${cArray.slice(0, 3).join(', ')}...]`;
                
                item.innerHTML = `
                    <div class="vault-item-header">
                        <span>${entry.site}</span>
                    </div>
                    <div class="vault-item-body">
                        <div>User: ${entry.username}</div>
                        <div class="math-toggle" onclick="this.nextElementSibling.style.display = this.nextElementSibling.style.display === 'none' ? 'block' : 'none'">Show/Hide RSA Math</div>
                        <div style="display:none; margin-top:0.5rem; padding:0.5rem; background:rgba(0,0,0,0.3); border-radius:5px;">
                            <div class="mono" style="font-size:0.8rem; color:var(--text-secondary);">Cipher (c): ${shortCipher}</div>
                            <div class="mono" style="font-size:0.8rem; color:var(--math-text); margin-top:0.3rem;">m = c^d (mod n)</div>
                            <div class="mono" style="font-size:0.9rem; color:white; margin-top:0.3rem;">Plaintext: ${entry.decrypted_password}</div>
                        </div>
                    </div>
                `;
                list.appendChild(item);
            });
        }
    } catch (e) {
        console.error(e);
    }
}

function truncate(numStr, len=15) {
    numStr = String(numStr);
    if (numStr.length > len * 2) {
        return numStr.substring(0, len) + '...' + numStr.substring(numStr.length - len);
    }
    return numStr;
}

let entropyChart = null;

function updateChart() {
    const useUpper = document.getElementById('gen-upper').checked;
    const useLower = document.getElementById('gen-lower').checked;
    const useDigits = document.getElementById('gen-digits').checked;
    const useSpecial = document.getElementById('gen-special').checked;
    
    let poolSize = 0;
    if (useLower) poolSize += 26;
    if (useUpper) poolSize += 26;
    if (useDigits) poolSize += 10;
    if (useSpecial) poolSize += 32;
    if (poolSize === 0) poolSize = 1;
    
    const bitsPerChar = Math.log2(poolSize);
    const labels = [];
    const dataPoints = [];
    const currentLen = parseInt(document.getElementById('gen-len').value) || 16;
    
    for (let l = 1; l <= 32; l++) {
        labels.push(l);
        dataPoints.push(parseFloat((bitsPerChar * l).toFixed(2)));
    }
    
    const ctx = document.getElementById('entropyChart').getContext('2d');
    
    if (entropyChart) {
        entropyChart.data.datasets[0].data = dataPoints;
        entropyChart.data.datasets[1].data = labels.map(l => l === currentLen ? bitsPerChar * l : null);
        entropyChart.update();
    } else {
        entropyChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Entropy (bits)',
                        data: dataPoints,
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.15)',
                        fill: true,
                        tension: 0.3,
                        pointRadius: 2,
                        borderWidth: 2
                    },
                    {
                        label: 'Your Password',
                        data: labels.map(l => l === currentLen ? bitsPerChar * l : null),
                        borderColor: '#22c55e',
                        backgroundColor: '#22c55e',
                        pointRadius: 8,
                        pointStyle: 'star',
                        showLine: false
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { labels: { color: '#f8fafc' } },
                    title: {
                        display: true,
                        text: 'How Password Length Affects Security',
                        color: '#f8fafc',
                        font: { size: 14, family: 'Outfit' }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const bits = context.raw;
                                if (bits === null) return '';
                                let strength = 'Very Weak';
                                if (bits >= 128) strength = 'Excellent';
                                else if (bits >= 80) strength = 'Strong';
                                else if (bits >= 60) strength = 'Good';
                                else if (bits >= 40) strength = 'Moderate';
                                return `${bits.toFixed(1)} bits — ${strength}`;
                            }
                        }
                    },
                    annotation: {}
                },
                scales: {
                    x: {
                        title: { display: true, text: 'Password Length (characters)', color: '#94a3b8', font: { family: 'Outfit' } },
                        ticks: { color: '#94a3b8' },
                        grid: { color: 'rgba(255,255,255,0.05)' }
                    },
                    y: {
                        title: { display: true, text: 'Entropy (bits) — higher = harder to crack', color: '#94a3b8', font: { family: 'Outfit' } },
                        ticks: { color: '#94a3b8' },
                        grid: { color: 'rgba(255,255,255,0.05)' },
                        beginAtZero: true
                    }
                }
            }
        });
    }
}

document.getElementById('gen-len').addEventListener('input', updateChart);
document.getElementById('gen-upper').addEventListener('change', updateChart);
document.getElementById('gen-lower').addEventListener('change', updateChart);
document.getElementById('gen-digits').addEventListener('change', updateChart);
document.getElementById('gen-special').addEventListener('change', updateChart);
