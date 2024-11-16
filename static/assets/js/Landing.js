// Typewriter Effect
const typewriterText = ['cybersecurity', 'data protection', 'digital safety'];
let currentText = 0;
let charIndex = 0;

function type() {
    const element = document.querySelector('.typewriter');
    if (charIndex < typewriterText[currentText].length) {
        element.innerHTML += typewriterText[currentText].charAt(charIndex);
        charIndex++;
        setTimeout(type, 100);
    } else {
        setTimeout(erase, 2000);
    }
}

function erase() {
    const element = document.querySelector('.typewriter');
    if (charIndex > 0) {
        element.innerHTML = typewriterText[currentText].substring(0, charIndex - 1);
        charIndex--;
        setTimeout(erase, 50);
    } else {
        currentText = (currentText + 1) % typewriterText.length;
        setTimeout(type, 500);
    }
}

document.addEventListener("DOMContentLoaded", type);

// Smooth Scrolling
document.querySelectorAll('.navbar a').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// Sticky Navbar & Active Link Highlighting
window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar');
    navbar.classList.toggle('sticky', window.scrollY > 0);

    const sections = document.querySelectorAll('section');
    const navLinks = document.querySelectorAll('.navbar a');
    let currentSection = '';

    sections.forEach(section => {
        const sectionTop = section.offsetTop - 50;
        if (pageYOffset >= sectionTop) {
            currentSection = section.getAttribute('id');
        }
    });

    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${currentSection}`) {
            link.classList.add('active');
        }
    });
});

// Scroll Animations (Intersection Observer)
const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('show');
        } else {
            entry.target.classList.remove('show');
        }
    });
}, { threshold: 0.2 });

document.querySelectorAll('.slide-in-left, .fade-in, .fade-in-up').forEach(el => {
    observer.observe(el);
});

// Counter Animation
const counters = document.querySelectorAll('[data-counter]');
let countersAnimated = false;

function animateCounters() {
    if (!countersAnimated) {
        counters.forEach(counter => {
            const updateCount = () => {
                const target = +counter.getAttribute('data-counter');
                const count = +counter.innerText;
                const increment = target / 100;

                if (count < target) {
                    counter.innerText = Math.ceil(count + increment);
                    setTimeout(updateCount, 30);
                } else {
                    counter.innerText = target;
                }
            };
            updateCount();
        });
        countersAnimated = true;
    }
}

window.addEventListener('scroll', () => {
    const aboutSection = document.getElementById('about');
    const offsetTop = aboutSection.offsetTop;
    if (window.scrollY > offsetTop - window.innerHeight + 100) {
        animateCounters();
    }
});

// Form Validation & Success Message
const form = document.querySelector('#contact form');
form.addEventListener('submit', (e) => {
    e.preventDefault();
    let isValid = true;

    form.querySelectorAll('input, textarea').forEach(input => {
        if (!input.value) {
            isValid = false;
            input.classList.add('error');
        } else {
            input.classList.remove('error');
        }
    });

    if (isValid) {
        alert('Thank you for your message! We will get back to you soon.');
        form.reset();
    }
});
