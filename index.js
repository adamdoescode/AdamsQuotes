
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
