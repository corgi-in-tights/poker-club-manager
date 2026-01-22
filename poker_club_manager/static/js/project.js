function copyUrl(btn) {
    const absoluteUrl = window.location.origin + btn.dataset.url;
    navigator.clipboard.writeText(absoluteUrl);
    btn.innerText = "URL Copied!";
    setTimeout(() => {
        btn.innerText = "Copy URL";
    }, 2000);
}
