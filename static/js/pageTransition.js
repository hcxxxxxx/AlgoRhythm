document.addEventListener('DOMContentLoaded', () => {
    // 为所有链接添加过渡效果
    document.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', function(e) {
            if (this.href && !this.href.includes('#')) {
                e.preventDefault();
                const container = document.querySelector('.container');
                container.classList.add('page-transition-exit');
                
                setTimeout(() => {
                    window.location.href = this.href;
                }, 500); // 与 CSS 动画时间相匹配
            }
        });
    });
});