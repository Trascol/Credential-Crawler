const form = document.getElementById('form');
const username_input = document.getElementById('username-input');
const email_input = document.getElementById('email-input');
const password_input = document.getElementById('password-input');
const repeat_password_input = document.getElementById('repeat-password-input');
const error_message = document.getElementById('error-message');

// Handle submission
form?.addEventListener('submit', (e) => {
    let errors = [];

    if (username_input) {
        // Signup
        errors = getSignupFormErrors();
    } else {
        // Login
        errors = getLoginFormErrors();
    }

    if (errors.length > 0) {
        e.preventDefault();
        error_message.innerText = errors.join('. ');
    }
});

// Validate signup
function getSignupFormErrors() {
    let errors = [];

    if (!username_input?.value.trim()) {
        errors.push('Username is required');
        username_input?.parentElement?.classList.add('incorrect');
    }

    if (!email_input?.value.trim()) {
        errors.push('Email is required');
        email_input?.parentElement?.classList.add('incorrect');
    }

    if (!password_input?.value.trim()) {
        errors.push('Password is required');
        password_input?.parentElement?.classList.add('incorrect');
    }

    if (password_input?.value.length < 8) {
        errors.push('Password must have at least 8 characters');
        password_input?.parentElement?.classList.add('incorrect');
    }

    if (password_input?.value !== repeat_password_input?.value) {
        errors.push('Passwords do not match');
        password_input?.parentElement?.classList.add('incorrect');
        repeat_password_input?.parentElement?.classList.add('incorrect');
    }

    return errors;
}

// Validate login
function getLoginFormErrors() {
    let errors = [];

    if (!email_input?.value.trim()) {
        errors.push('Email is required');
        email_input?.parentElement?.classList.add('incorrect');
    }

    if (!password_input?.value.trim()) {
        errors.push('Password is required');
        password_input?.parentElement?.classList.add('incorrect');
    }

    return errors;
}

// Remove error styles on input
const allInputs = [username_input, email_input, password_input, repeat_password_input].filter(Boolean);
allInputs.forEach(input => {
    input.addEventListener('input', () => {
        input.parentElement?.classList.remove('incorrect');
        error_message.innerText = '';
    });
});
