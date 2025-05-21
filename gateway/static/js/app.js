// Función para verificar si el usuario está autenticado
function checkAuth() {
    const token = localStorage.getItem('token');
    console.log("Token actual:", token);
    const publicPages = ['/', '/login'];
    
    // Si no estamos en una página pública y no hay token, redirigir al login
    if (!publicPages.includes(window.location.pathname) && !token) {
        console.log("Redirigiendo a login por falta de token");
        window.location.href = '/login';
        return false;
    }
    return true;
}

// Función para interceptar todas las solicitudes fetch y añadir el token
function setupFetchInterceptor() {
    const originalFetch = window.fetch;
    window.fetch = function(url, options = {}) {
        const token = localStorage.getItem('token');
        
        // Si hay un token y no es una solicitud a /api/login
        if (token && !url.includes('/api/login')) {
            options = options || {};
            options.headers = options.headers || {};
            options.headers['Authorization'] = `Bearer ${token}`;
            console.log("Añadiendo token a la solicitud:", url);
        }
        
        return originalFetch(url, options);
    };
}

// Ejecutar al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    // Configurar interceptor de fetch
    setupFetchInterceptor();
    
    // Verificar autenticación
    if (!checkAuth()) return;
    
    // Agregar evento para cerrar sesión
    const logoutLink = document.createElement('li');
    logoutLink.innerHTML = '<a href="#" id="logoutBtn">Cerrar Sesión</a>';
    
    // Si el usuario está autenticado, mostrar el botón de cerrar sesión
    if (localStorage.getItem('token')) {
        const menuElement = document.querySelector('.menu');
        if (menuElement) {
            menuElement.appendChild(logoutLink);
            
            document.getElementById('logoutBtn').addEventListener('click', function(e) {
                e.preventDefault();
                localStorage.removeItem('token');
                window.location.href = '/login';
            });
        }
    }
});
