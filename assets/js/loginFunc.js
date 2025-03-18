$(document).ready(function () {
    const API_BASE_URL = "https://credential-crawler-backend.onrender.com";
    const userNameDisplay = $('#user-name');
    const logoutBtn = $('#logout-btn');
    const loginLink = $('.login-link');
    const registerLink = $('.register-link');
    const guestUser = $('#guest_user');
    const verifiedUser = $('#verified_user');


    function updateAuthUI() {
        const user = JSON.parse(localStorage.getItem('user'));

        if (user && user.name) {
          userNameDisplay.text(`Welcome, ${user.name}`);
          //  userNameDisplay.show();
          //  logoutBtn.show();
          //  loginLink.hide();
          //  registerLink.hide();
          guestUser.hide();
          verifiedUser.show();
        } else {
          //  userNameDisplay.hide();
          //  logoutBtn.hide();
          //  loginLink.show();
          //  registerLink.show();
          guestUser.show();
          verifiedUser.hide();
        }
    }

    function handleLogout() {
        localStorage.removeItem('user');
        updateAuthUI();
        window.location.href = "index.html";
    }

    logoutBtn.on('click', handleLogout);

    // Run on page load
    updateAuthUI();
});
