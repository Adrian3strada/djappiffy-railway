document.addEventListener('DOMContentLoaded', function () {
    const textareas = document.querySelectorAll('textarea[name="description"]');
    textareas.forEach(textarea => {
        textarea.style.height = Math.min(textarea.scrollHeight, 12 * parseFloat(getComputedStyle(textarea).lineHeight)) + 'px';

        textarea.addEventListener('input', function () {
            this.style.height = '';
            this.style.height = Math.min(this.scrollHeight, 12 * parseFloat(getComputedStyle(this).lineHeight)) + 'px';
        });
    });
});
