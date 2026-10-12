
// Toggle the table of contents, which starts hidden in Header.html.
function handleClick() {
    const tableOfContents = document.querySelector('.tableOfContentsDiv');
    const button = document.querySelector('.hideTableOfContents');
    tableOfContents.hidden = !tableOfContents.hidden;
    button.setAttribute('aria-expanded', String(!tableOfContents.hidden));
    button.textContent = tableOfContents.hidden
        ? 'Show Table of Contents'
        : 'Hide Table of Contents';
}

// Add handleClick function to button with class hideTableOfContents.
document.querySelector('.hideTableOfContents').addEventListener('click', handleClick);

// Collapse a quote to its title when its header row (title or chevron) is clicked.
document.addEventListener('click', (event) => {
    const header = event.target.closest('.quote-header');
    if (!header) {
        return;
    }
    const quote = header.closest('.quote');
    const button = header.querySelector('.quote-toggle');
    const collapsed = quote.classList.toggle('is-collapsed');
    button.setAttribute('aria-expanded', String(!collapsed));
    button.setAttribute('aria-label', collapsed ? 'Expand quote' : 'Collapse quote');
});
