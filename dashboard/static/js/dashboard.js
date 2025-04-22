// Dashboard functionality
document.addEventListener('DOMContentLoaded', function() {
    // Enable tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))
    
    // Enable popovers
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]')
    const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl))
    
    // Add active class to current nav item
    const currentLocation = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentLocation) {
            link.classList.add('active');
        }
    });
});

// Function to format numbers with commas
function formatNumber(num) {
    return num.toString().replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,');
}

// Function to update stats via API
function updateStats() {
    // Check if we're on the dashboard page
    const statsElements = document.getElementById('total-users');
    if (!statsElements) return;
    
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            // Update stats display
            document.getElementById('total-users').textContent = formatNumber(data.system.total_users);
            document.getElementById('total-deliveries').textContent = formatNumber(data.system.total_deliveries);
            document.getElementById('total-earnings').textContent = formatNumber(data.system.total_earnings);
            document.getElementById('active-buffs').textContent = data.system.active_buffs;
            
            // Update top users table if it exists
            const topUsersTable = document.getElementById('top-users-table');
            if (topUsersTable && data.top_users) {
                let html = '';
                data.top_users.forEach((user, index) => {
                    const medal = index < 3 
                        ? (index === 0 ? '🥇' : (index === 1 ? '🥈' : '🥉')) 
                        : (index + 1);
                    
                    html += `
                        <tr>
                            <td>${medal}</td>
                            <td>${user.username}</td>
                            <td>${user.deliveries}</td>
                        </tr>
                    `;
                });
                
                if (data.top_users.length === 0) {
                    html = '<tr><td colspan="3" class="text-center">Нет данных о доставках</td></tr>';
                }
                
                topUsersTable.innerHTML = html;
            }
        })
        .catch(error => console.error('Error fetching stats:', error));
}

// Update stats every 30 seconds
setInterval(updateStats, 30000);
