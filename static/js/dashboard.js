// Dashboard JavaScript for Telegram Delivery Bot

// Format numbers with commas for thousands
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Format seconds to days, hours, minutes, seconds
function formatUptime(seconds) {
    const days = Math.floor(seconds / (3600 * 24));
    const hours = Math.floor((seconds % (3600 * 24)) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    let result = '';
    if (days > 0) result += `${days}д `;
    if (hours > 0) result += `${hours}ч `;
    if (minutes > 0) result += `${minutes}м `;
    if (secs > 0 || result === '') result += `${secs}с`;
    
    return result.trim();
}

// Update stats from API
function updateStats() {
    fetch('/api/stats')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Update bot stats if the data exists
            if (data.bot) {
                document.getElementById('users-count').textContent = formatNumber(data.bot.total_users);
                document.getElementById('deliveries-count').textContent = formatNumber(data.bot.total_deliveries);
                document.getElementById('earnings-count').textContent = formatNumber(data.bot.total_earnings) + ' руб.';
                document.getElementById('buffs-count').textContent = formatNumber(data.bot.active_buffs);
            }
            
            // Update top users if data exists
            const topUsersList = document.getElementById('top-users-list');
            if (data.top_users && data.top_users.length > 0 && topUsersList) {
                topUsersList.innerHTML = '';
                
                data.top_users.forEach((user, i) => {
                    let medal = '';
                    if (i === 0) medal = '🥇';
                    else if (i === 1) medal = '🥈';
                    else if (i === 2) medal = '🥉';
                    else medal = `${i+1}.`;
                    
                    const li = document.createElement('li');
                    li.className = 'list-group-item d-flex justify-content-between align-items-center';
                    li.innerHTML = `
                        <span>${medal} <strong>${user.username}</strong></span>
                        <span class="badge bg-primary rounded-pill">${user.deliveries} доставок</span>
                    `;
                    topUsersList.appendChild(li);
                });
            }
            
            // Update system stats if the data exists
            if (data.system) {
                const cpuBar = document.getElementById('cpu-usage');
                if (cpuBar) {
                    cpuBar.style.width = `${data.system.cpu}%`;
                    cpuBar.textContent = `${data.system.cpu}%`;
                }
                
                const memoryBar = document.getElementById('memory-usage');
                if (memoryBar) {
                    memoryBar.style.width = `${data.system.memory}%`;
                    memoryBar.textContent = `${data.system.memory}%`;
                }
                
                const diskBar = document.getElementById('disk-usage');
                if (diskBar) {
                    diskBar.style.width = `${data.system.disk}%`;
                    diskBar.textContent = `${data.system.disk}%`;
                }
                
                const uptimeElem = document.getElementById('uptime');
                if (uptimeElem) {
                    uptimeElem.textContent = formatUptime(data.system.uptime);
                }
            }
            
            // Update bot status
            const statusElem = document.getElementById('bot-status');
            if (statusElem) {
                if (data.bot_status) {
                    statusElem.innerHTML = '<span class="badge bg-success">Онлайн</span>';
                } else {
                    statusElem.innerHTML = '<span class="badge bg-danger">Оффлайн</span>';
                }
            }
        })
        .catch(error => {
            console.error('Error fetching stats:', error);
        });
}

// Update stats every 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    // Initial update
    updateStats();
    
    // Set interval for updates
    setInterval(updateStats, 5000);
});