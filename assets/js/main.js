/*
	Strongly Typed by HTML5 UP
	html5up.net | @ajlkn
	Free for personal and commercial use under the CCA 3.0 license (html5up.net/license)
*/

(function($) {

	var	$window = $(window),
		$body = $('body');

	// Breakpoints.
		breakpoints({
			xlarge:  [ '1281px',  '1680px' ],
			large:   [ '981px',   '1280px' ],
			medium:  [ '737px',   '980px'  ],
			small:   [ null,      '736px'  ]
		});

	// Play initial animations on page load.
		$window.on('load', function() {
			window.setTimeout(function() {
				$body.removeClass('is-preload');
			}, 100);
		});

	// Dropdowns.
		$('#nav > ul').dropotron({
			mode: 'fade',
			noOpenerFade: true,
			hoverDelay: 150,
			hideDelay: 350
		});

	// Nav.

		// Title Bar.
			$(
				'<div id="titleBar">' +
					'<a href="#navPanel" class="toggle"></a>' +
				'</div>'
			)
				.appendTo($body);

		// Panel.
			$(
				'<div id="navPanel">' +
					'<nav>' +
						$('#nav').navList() +
					'</nav>' +
				'</div>'
			)
				.appendTo($body)
				.panel({
					delay: 500,
					hideOnClick: true,
					hideOnSwipe: true,
					resetScroll: true,
					resetForms: true,
					side: 'left',
					target: $body,
					visibleClass: 'navPanel-visible'
				});

})(jQuery);


$(document).ready(function () {
    const API_BASE_URL = "https://credential-crawler-backend.onrender.com";
    const userNameDisplay = $('#user-name');
    const logoutBtn = $('#logout-btn');
    const loginLink = $('.login-link');
    const registerLink = $('.register-link');

    function updateAuthUI() {
        const user = JSON.parse(localStorage.getItem('user'));

        if (user && user.name) {
            userNameDisplay.text(`Welcome, ${user.name}`);
            userNameDisplay.show();
            logoutBtn.show();
            loginLink.hide();
            registerLink.hide();
        } else {
            userNameDisplay.hide();
            logoutBtn.hide();
            loginLink.show();
            registerLink.show();
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
