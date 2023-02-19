
// click button hides the div of class tableOfContentsDiv
function handleClick() {
    if (document.querySelector('.tableOfContentsDiv').style.display === 'none') {
        document.querySelector('.tableOfContentsDiv').style.display = '';
        document.querySelector('.hideTableOfContents').innerHTML = 'Hide table of Contents';
    } else {
        document.querySelector('.tableOfContentsDiv').style.display = 'none';
        document.querySelector('.hideTableOfContents').innerHTML = 'Show table of Contents';
    }
    }

// add handleClick function to button with class hideTableOfContents
document.querySelector('.hideTableOfContents').addEventListener('click', handleClick);
