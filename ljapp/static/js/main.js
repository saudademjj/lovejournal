(function(){
function initBasePage(){
    window.addEventListener('load', function () {
                const pre = document.getElementById('preloader');
                if (!pre) return;
                pre.classList.add('preloader--hidden');
                setTimeout(() => pre.remove(), 900);
            });
}


function initIndexPage(props) {
    const prefersReducedMotion =
            window.matchMedia &&
            window.matchMedia('(prefers-reduced-motion: reduce)').matches;

        let lenisInstance = null;
        const selectedTag = props.selectedTag || '';
        const filterType = props.filterType || 'all';

        /* Cursor glow */
        const cursorGlow = document.getElementById('cursor-glow');
        let mouseX = window.innerWidth / 2;
        let mouseY = window.innerHeight / 2;
        let currentX = mouseX;
        let currentY = mouseY;

        if (cursorGlow) {
            document.addEventListener('mousemove', (e) => {
                mouseX = e.clientX;
                mouseY = e.clientY;
            });

            (function animateCursor() {
                currentX += (mouseX - currentX) * 0.12;
                currentY += (mouseY - currentY) * 0.12;
                cursorGlow.style.left = currentX + 'px';
                cursorGlow.style.top = currentY + 'px';
                if (!prefersReducedMotion) requestAnimationFrame(animateCursor);
            })();
        }

        /* Hearts canvas */
        const canvas = document.getElementById('hearts-canvas');
        const ctx = canvas.getContext('2d');
        let hearts = [];
        let isAnimatingHearts = false;

        function resizeCanvas() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }
        window.addEventListener('resize', resizeCanvas);
        resizeCanvas();

        function triggerHearts() {
            const originX = window.innerWidth / 2;
            const originY = window.innerHeight - 80;
            for (let i = 0; i < 26; i++) {
                hearts.push({
                    x: originX,
                    y: originY,
                    size: Math.random() * 20 + 6,
                    speedX: (Math.random() - 0.5) * 12,
                    speedY: Math.random() * -15 - 6,
                    opacity: 1,
                    rotation: Math.random() * 360
                });
            }
            if (!isAnimatingHearts) {
                isAnimatingHearts = true;
                animateHearts();
            }
        }
        window.triggerHearts = triggerHearts;

        function animateHearts() {
            if (hearts.length === 0) {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                isAnimatingHearts = false;
                return;
            }
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            hearts.forEach((h, i) => {
                h.x += h.speedX;
                h.y += h.speedY;
                h.speedY += 0.35;
                h.opacity -= 0.012;

                ctx.save();
                ctx.translate(h.x, h.y);
                ctx.rotate(h.rotation);
                ctx.fillStyle = 'rgba(255,0,60,' + h.opacity + ')';
                ctx.font = h.size + 'px serif';
                ctx.fillText('❤', -h.size / 2, h.size / 2);
                ctx.restore();

                if (h.opacity <= 0) hearts.splice(i, 1);
            });
            requestAnimationFrame(animateHearts);
        }

        /* Modal + geocode */
        const modal = document.getElementById('input-modal');
        const backdrop = document.getElementById('modal-backdrop');
        const dateInput = document.getElementById('date-input');
        const form = document.getElementById('modal-form');
        const fields = document.getElementById('dynamic-fields');
        const titleEl = document.getElementById('modal-title');

        function syncNowToDateInput() {
            if (!dateInput) return;
            const now = new Date();
            now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
            dateInput.value = now.toISOString().slice(0, 16);
        }

        function setupGeoHelper(scope) {
            const container = scope || document;
            const geoBtn = container.querySelector('.geo-btn');
            const locInput = container.querySelector('input[name="location"]');
            const coordsInput = container.querySelector('input[name="location_coords"]');
            const statusEl = container.querySelector('.geo-status');
            if (!geoBtn || !locInput || !coordsInput) return;

            geoBtn.addEventListener('click', async () => {
                const query = (locInput.value || '').trim();
                if (!query) {
                    if (statusEl) statusEl.textContent = '输入地点';
                    return;
                }
                if (statusEl) statusEl.textContent = 'Searching...';

                try {
                    const url = 'https://restapi.amap.com/v3/geocode/geo?key=fd67dbc2f43a792a5a2aa190e3a49d92&address=' + encodeURIComponent(query);
                    const res = await fetch(url);
                    const data = await res.json();
                    if (data.status !== '1' || !data.geocodes || !data.geocodes.length) {
                        if (statusEl) statusEl.textContent = '未找到';
                        return;
                    }
                    const loc = data.geocodes[0].location; // "lng,lat"
                    const parts = loc.split(',');
                    if (parts.length !== 2) {
                        if (statusEl) statusEl.textContent = '坐标错误';
                        return;
                    }
                    const lng = parseFloat(parts[0]);
                    const lat = parseFloat(parts[1]);
                    if (isNaN(lat) || isNaN(lng)) {
                        if (statusEl) statusEl.textContent = '坐标错误';
                        return;
                    }
                    coordsInput.value = lat.toFixed(6) + ',' + lng.toFixed(6);
                    if (statusEl) statusEl.textContent = '已匹配';
                } catch (e) {
                    if (statusEl) statusEl.textContent = '网络错误';
                }
            });
        }

        function openModal(type) {
            if (!modal) return;
            syncNowToDateInput();
            fields.innerHTML = '';
            form.action = '';
            form.onsubmit = null;

            backdrop.classList.add('active');
            modal.showModal();
            document.documentElement.classList.add('modal-open');
            if (lenisInstance) lenisInstance.stop();

            if (type === 'entry') {
        form.action = props.addEntryUrl || '/add/entry';
                titleEl.innerText = 'THOUGHT';
                fields.innerHTML = `
                    <textarea
                        name="content"
                        rows="5"
                        class="modal-field"
                        placeholder="..."
                        style="resize:vertical;"
                        required
                    ></textarea>
                    <div class="geo-row">
                        <input
                            name="location"
                            placeholder="Where (optional)"
                            class="modal-field"
                        >
                        <button type="button" class="geo-btn">AUTO</button>
                    </div>
                    <div class="geo-status"></div>
                    <input type="hidden" name="location_coords">
                `;
                setupGeoHelper(fields);
            } else if (type === 'keydate') {
            form.action = props.addKeydateUrl || '/add/keydate';
                titleEl.innerText = 'MEMORY';
                fields.innerHTML = `
                    <input
                        name="title"
                        placeholder="Title"
                        class="modal-field"
                        required
                    >
                    <input type="hidden" name="date" id="kd-hidden">
                    <div class="geo-row">
                        <input
                            name="location"
                            placeholder="Where (optional)"
                            class="modal-field"
                        >
                        <button type="button" class="geo-btn">AUTO</button>
                    </div>
                    <div class="geo-status"></div>
                    <input type="hidden" name="location_coords">
                `;
                setupGeoHelper(fields);
                form.onsubmit = function () {
                    const hidden = document.getElementById('kd-hidden');
                    if (hidden && dateInput) hidden.value = dateInput.value;
                };
            } else if (type === 'photo') {
            form.action = props.addPhotoUrl || '/add/photo';
                titleEl.innerText = 'VISUAL';
                fields.innerHTML = `
                    <input
                        type="file"
                        name="photo"
                        class="modal-field"
                        accept="image/*"
                        required
                    >
                    <input
                        name="caption"
                        placeholder="Caption"
                        class="modal-field"
                        style="margin-top:6px"
                    >
                    <div class="geo-row">
                        <input
                            name="location"
                            placeholder="Where (optional)"
                            class="modal-field"
                        >
                        <button type="button" class="geo-btn">AUTO</button>
                    </div>
                    <div class="geo-status"></div>
                    <input type="hidden" name="location_coords">
                `;
                setupGeoHelper(fields);
            }
        }
        window.openModal = openModal;

        function openEditModal(button) {
            if (!modal) return;
            const type = button.dataset.editType;
            const id = button.dataset.editId;
            const timestamp = button.dataset.editTimestamp || '';
            const location = button.dataset.editLocation || '';

            fields.innerHTML = '';
            form.action = '';
            form.onsubmit = null;

            if (timestamp && dateInput) {
                dateInput.value = timestamp;
            } else {
                syncNowToDateInput();
            }

            backdrop.classList.add('active');
            modal.showModal();
            document.documentElement.classList.add('modal-open');
            if (lenisInstance) lenisInstance.stop();

            titleEl.innerText = 'EDIT';
            form.action = `/edit/${type}/${id}`;

            if (type === 'entry') {
                fields.innerHTML = `
                    <textarea
                        name="content"
                        rows="5"
                        class="modal-field"
                        style="resize:vertical;"
                        required
                    ></textarea>
                    <div class="geo-row">
                        <input
                            name="location"
                            placeholder="Where (optional)"
                            class="modal-field"
                        >
                        <button type="button" class="geo-btn">AUTO</button>
                    </div>
                    <div class="geo-status"></div>
                    <input type="hidden" name="location_coords">
                `;
                const textarea = fields.querySelector('textarea[name="content"]');
                const locInput = fields.querySelector('input[name="location"]');
                textarea.value = button.dataset.editContent || '';
                locInput.value = location || '';
                setupGeoHelper(fields);
            } else if (type === 'keydate') {
                fields.innerHTML = `
                    <input
                        name="title"
                        class="modal-field"
                        required
                    >
                    <input type="hidden" name="date" id="kd-hidden">
                    <div class="geo-row">
                        <input
                            name="location"
                            placeholder="Where (optional)"
                            class="modal-field"
                        >
                        <button type="button" class="geo-btn">AUTO</button>
                    </div>
                    <div class="geo-status"></div>
                    <input type="hidden" name="location_coords">
                `;
                const titleInput = fields.querySelector('input[name="title"]');
                const locInput = fields.querySelector('input[name="location"]');
                const hidden = fields.querySelector('#kd-hidden');
                titleInput.value = button.dataset.editTitle || '';
                locInput.value = location || '';
                if (hidden && dateInput) hidden.value = dateInput.value;
                form.onsubmit = function () {
                    const hidden = document.getElementById('kd-hidden');
                    if (hidden && dateInput) hidden.value = dateInput.value;
                };
                setupGeoHelper(fields);
            } else if (type === 'photo') {
                fields.innerHTML = `
                    <input
                        type="file"
                        name="photo"
                        class="modal-field"
                        accept="image/*"
                    >
                    <input
                        name="caption"
                        placeholder="Caption"
                        class="modal-field"
                        style="margin-top:6px"
                    >
                    <div class="geo-row">
                        <input
                            name="location"
                            placeholder="Where (optional)"
                            class="modal-field"
                        >
                        <button type="button" class="geo-btn">AUTO</button>
                    </div>
                    <div class="geo-status"></div>
                    <input type="hidden" name="location_coords">
                `;
                const captionInput = fields.querySelector('input[name="caption"]');
                const locInput = fields.querySelector('input[name="location"]');
                captionInput.value = button.dataset.editCaption || '';
                locInput.value = location || '';
                setupGeoHelper(fields);
            }
        }

        function closeModal() {
            if (!modal) return;
            backdrop.classList.remove('active');
            modal.close();
            document.documentElement.classList.remove('modal-open');
            if (lenisInstance) lenisInstance.start();
        }
        window.closeModal = closeModal;

        if (backdrop) backdrop.addEventListener('click', closeModal);

        /* Lenis smooth scroll */
        if (!prefersReducedMotion && typeof Lenis !== 'undefined') {
            const lenis = new Lenis({
                lerp: 0.12,
                smoothWheel: true,
                smoothTouch: false,
                wheelMultiplier: 1.1
            });
            lenisInstance = lenis;
            function raf(time) {
                lenis.raf(time);
                requestAnimationFrame(raf);
            }
            requestAnimationFrame(raf);
        }

        /* GSAP timeline reveal + typewriter + 照片视差 */
        function enhanceTimelineRows(root) {
            const scope = root || document;
            if (prefersReducedMotion || typeof gsap === 'undefined' || typeof ScrollTrigger === 'undefined') {
                scope.querySelectorAll('.time-wrapper, .content-wrapper').forEach(el => {
                    el.style.opacity = 1;
                    el.style.transform = 'none';
                });
                return;
            }
            const rows = scope.querySelectorAll('.timeline-row:not([data-animated])');
            rows.forEach((row) => {
                row.dataset.animated = '1';
                const timeCol = row.querySelector('.time-wrapper');
                const contentCol = row.querySelector('.content-wrapper');
                const dot = row.querySelector('.axis-dot');
                const photo = row.querySelector('.photo-frame');
                const isEven = row.classList.contains('even');

                const tl = gsap.timeline({
                    scrollTrigger: {
                        trigger: row,
                        start: 'top 80%',
                        end: 'bottom 40%',
                        toggleActions: 'play none none reverse'
                    }
                });

                tl.fromTo(
                    timeCol,
                    { opacity: 0, y: 26 },
                    { opacity: 1, y: 0, duration: 0.7, ease: 'power3.out' },
                    0
                ).fromTo(
                    contentCol,
                    { opacity: 0, y: 32 },
                    { opacity: 1, y: 0, duration: 0.8, ease: 'power3.out' },
                    0.05
                ).fromTo(
                    dot,
                    { scale: 0.7, opacity: 0.5 },
                    { scale: 1, opacity: 1, duration: 0.6, ease: 'back.out(1.7)' },
                    0.1
                );

                if (photo) {
                    gsap.to(photo, {
                        y: isEven ? -14 : 14,
                        ease: 'none',
                        scrollTrigger: {
                            trigger: row,
                            start: 'top bottom',
                            end: 'bottom top',
                            scrub: true
                        }
                    });
                }
            });

            initTypewriter(scope);
        }
    /* ===== 顶部 HUD 时钟 + 时间轴高亮联动 ===== */
        const timelineGrid = document.querySelector('.timeline-grid');
        const hudClock = document.getElementById('hud-clock');

        let hudTimer = null;
        let activeRow = null;
        let hudMode = 'now';   // 'now' | 'memory'

        function setHudHighlight(isActive) {
            if (!hudClock) return;
            hudClock.classList.toggle('hud-clock--highlight', !!isActive);
        }

        function revealHudClock() {
            if (!hudClock) return;
            if (prefersReducedMotion) {
                hudClock.classList.add('hud-clock--visible');
                return;
            }
            requestAnimationFrame(() => hudClock.classList.add('hud-clock--visible'));
        }

        function ensureLabelSpans(container) {
            if (!container) return null;
            let dateSpan = container.querySelector('.hud-date');
            let timeSpan = container.querySelector('.hud-time');
            const needsReset = !dateSpan || !timeSpan || container.children.length < 2;

            if (needsReset) {
                container.innerHTML = '';
                dateSpan = document.createElement('span');
                dateSpan.className = 'hud-date';
                timeSpan = document.createElement('span');
                timeSpan.className = 'hud-time';
                container.appendChild(dateSpan);
                container.appendChild(timeSpan);
            }

            return { dateSpan, timeSpan };
        }

        function ensureHudSpans() {
            if (!hudClock) return null;
            hudClock.dataset.controlled = 'true';
            return ensureLabelSpans(hudClock);
        }
        ensureHudSpans();

        function getRowTimestamp(row) {
            const dateText = row?.dataset?.date || row?.querySelector('.hud-date, .date-part')?.textContent || '';
            const timeText = row?.dataset?.time || row?.querySelector('.hud-time, .time-part')?.textContent || '';
            return {
                dateText: dateText.trim(),
                timeText: timeText.trim(),
            };
        }

        /** 统一更新 HUD 显示 - 只更新文本，不创建新元素 */
        function renderHud(dateText, timeText) {
            const spans = ensureHudSpans();
            if (!spans) return;
            spans.dateSpan.textContent = dateText || '';
            spans.timeSpan.textContent = timeText || '';
        }

        /** 获取当前实时时间 */
        function getRealTime() {
            const now = new Date();
            const pad = (n) => String(n).padStart(2, '0');
            return {
                date: `${now.getFullYear()}.${pad(now.getMonth() + 1)}.${pad(now.getDate())}`,
                time: `${pad(now.getHours())}:${pad(now.getMinutes())}`,
            };
        }

        /** 显示实时时间 */
        function renderHudNow() {
            const { date, time } = getRealTime();
            renderHud(date, time);
        }

        /** 进入"实时时间"模式 */
        function enterNowMode() {
            hudMode = 'now';
            if (!hudClock) return;

            setHudHighlight(false);

            // 清除旧定时器
            if (hudTimer) {
                clearInterval(hudTimer);
                hudTimer = null;
            }

            // 立即显示一次
            renderHudNow();

            // 每秒更新
            hudTimer = setInterval(() => {
                if (hudMode !== 'now') return;
                renderHudNow();
            }, 1000);
        }

        /** 显示时间轴记录的时间（停止实时走时） */
        function showHudForRow(row) {
            if (!hudClock || !row) return;

            hudMode = 'memory';

            // 停止实时更新
            if (hudTimer) {
                clearInterval(hudTimer);
                hudTimer = null;
            }

            const { dateText, timeText } = getRowTimestamp(row);
            renderHud(dateText, timeText);
        }

        /** 设置高亮行 */
        function setActiveRow(row) {
            if (activeRow === row) return;

            // 移除旧高亮
            if (activeRow) {
                activeRow.classList.remove('timeline-row--active');
            }

            activeRow = row;

            // 添加新高亮并更新 HUD
            if (row) {
                row.classList.add('timeline-row--active');
                setHudHighlight(true);
                showHudForRow(row);
            } else {
                setHudHighlight(false);
                enterNowMode();
            }
        }

        /** 绑定时间轴 hover 事件 - 绑定到整个 row 而不是单独的元素 */
        function bindTimelineHover(root) {
            const scope = root || document;
            const rows = scope.querySelectorAll('.timeline-row:not([data-hover-bound])');

            rows.forEach((row) => {
                row.dataset.hoverBound = '1';

                // 关键修复：监听整个 row 的 hover，而不是分别监听左右两侧
                row.addEventListener('mouseenter', () => {
                    setActiveRow(row);
                    if (cursorGlow) cursorGlow.classList.add('cursor-glow--active');
                });

                row.addEventListener('mouseleave', () => {
                    setActiveRow(null);
                    if (cursorGlow) cursorGlow.classList.remove('cursor-glow--active');
                });

                row.addEventListener('focusin', () => setActiveRow(row));
                row.addEventListener('focusout', (e) => {
                    if (!row.contains(e.relatedTarget)) setActiveRow(null);
                });
            });
        }

        // ===== 初始化 =====
        revealHudClock();
        enterNowMode();  // 先进入实时时间模式
        if (timelineGrid) {
            bindTimelineHover(document);
        }



        /* 磁吸效果：只作用在 axis-dot / dock 按钮等，不再影响 entry-card */
        function initMagneticElements(root) {
            if (typeof gsap === 'undefined') return;
            const scope = root || document;
            const magneticItems = scope.querySelectorAll('[data-magnetic]:not([data-magnetic-initialized])');
            magneticItems.forEach((item) => {
                item.dataset.magneticInitialized = '1';
                const strength = parseFloat(item.dataset.magneticStrength || '0.25');
                let bounds;
                function onMouseMove(e) {
                    if (!bounds) bounds = item.getBoundingClientRect();
                    const relX = e.clientX - (bounds.left + bounds.width / 2);
                    const relY = e.clientY - (bounds.top + bounds.height / 2);
                    gsap.to(item, {
                        x: relX * strength,
                        y: relY * strength,
                        duration: 0.5,
                        ease: 'power3.out'
                    });
                }
                function reset() {
                    bounds = null;
                    gsap.to(item, {
                        x: 0,
                        y: 0,
                        duration: 0.8,
                        ease: 'elastic.out(1.1, 0.4)'
                    });
                }
                item.addEventListener('mouseenter', () => {
                    bounds = item.getBoundingClientRect();
                    window.addEventListener('mousemove', onMouseMove);
                });
                item.addEventListener('mouseleave', () => {
                    window.removeEventListener('mousemove', onMouseMove);
                    reset();
                });
            });
        }
        initMagneticElements(document);

        /* 搜索 / 类型过滤 / 标签过滤：全部通过 URL 参数刷新 */
        const searchForm = document.getElementById('timeline-search-form');
        if (searchForm) {
            searchForm.addEventListener('submit', (e) => {
                e.preventDefault();
                const formData = new FormData(searchForm);
                const params = new URLSearchParams(window.location.search);
                params.delete('page');
                const q = (formData.get('q') || '').trim();
                if (q) params.set('q', q); else params.delete('q');
                const type = formData.get('type');
                if (type && type !== 'all') params.set('type', type); else params.delete('type');
                const tag = formData.get('tag');
                if (tag) params.set('tag', tag);
                window.location.search = params.toString();
            });
        }

        document.querySelectorAll('.filter-pill').forEach((pill) => {
            pill.addEventListener('click', () => {
                const type = pill.dataset.filter;
                const params = new URLSearchParams(window.location.search);
                params.delete('page');
                if (type === 'all') params.delete('type');
                else params.set('type', type);
                const qInput = searchForm && searchForm.querySelector('input[name="q"]');
                if (qInput && qInput.value.trim()) params.set('q', qInput.value.trim());
                if (selectedTag) params.set('tag', selectedTag);
                window.location.search = params.toString();
            });
        });

        document.querySelectorAll('.tag-chip').forEach((chip) => {
            chip.addEventListener('click', () => {
                const tag = chip.dataset.tag;
                const params = new URLSearchParams(window.location.search);
                params.delete('page');
                if (chip.classList.contains('tag-chip--active')) {
                    params.delete('tag');
                } else {
                    params.set('tag', tag);
                }
                const qInput = searchForm && searchForm.querySelector('input[name="q"]');
                if (qInput && qInput.value.trim()) params.set('q', qInput.value.trim());
                const typeInput = searchForm && searchForm.querySelector('input[name="type"]');
                if (typeInput && typeInput.value) params.set('type', typeInput.value);
                window.location.search = params.toString();
            });
        });

        /* 年份电梯：点击滚动 + IntersectionObserver 自动高亮 */
        const yearButtons = document.querySelectorAll('.year-pill');
        function scrollToRow(row) {
            if (!row) return;
            if (lenisInstance && typeof lenisInstance.scrollTo === 'function') {
                lenisInstance.scrollTo(row, { offset: -160 });
            } else {
                const top = row.getBoundingClientRect().top + window.scrollY - 160;
                window.scrollTo({ top, behavior: 'smooth' });
            }
        }
        yearButtons.forEach((btn) => {
            btn.addEventListener('click', () => {
                const targetYear = btn.dataset.year;
                const targetRow = document.querySelector(`.timeline-row[data-year="${targetYear}"]`);
                if (targetRow) scrollToRow(targetRow);
            });
        });
        function setActiveYear(year) {
            yearButtons.forEach((btn) => {
                btn.classList.toggle('year-pill--active', btn.dataset.year === String(year));
            });
        }
        if ('IntersectionObserver' in window) {
            const io = new IntersectionObserver((entries) => {
                let candidate = null;
                entries.forEach((entry) => {
                    if (!entry.isIntersecting) return;
                    const year = entry.target.dataset.year;
                    if (!candidate || entry.boundingClientRect.top < candidate.top) {
                        candidate = { year, top: entry.boundingClientRect.top };
                    }
                });
                if (candidate && candidate.year) setActiveYear(candidate.year);
            }, { threshold: 0.35 });
            document.querySelectorAll('.timeline-row').forEach((row) => io.observe(row));
        }

        /* 编辑按钮绑定 */
        function bindEditButtons(root) {
            const scope = root || document;
            const editButtons = scope.querySelectorAll('.btn-edit:not([data-edit-bound])');
            editButtons.forEach((btn) => {
                btn.dataset.editBound = '1';
                btn.addEventListener('click', () => openEditModal(btn));
            });
        }
        bindEditButtons(document);

        /* 打字机效果：短文本 Entry */
        function runTypewriter(el) {
            const text = el.dataset.fullText || '';
            el.textContent = '';
            let index = 0;
            const speed = 30;
            function step() {
                if (index >= text.length) return;
                el.textContent += text[index++];
                setTimeout(step, speed);
            }
            step();
        }

        function initTypewriter(root) {
            const scope = root || document;
            const targets = scope.querySelectorAll('.entry-body[data-typewriter="1"]:not([data-typewriter-init])');
            if (!targets.length) return;
            targets.forEach(el => {
                el.dataset.typewriterInit = '1';
                el.dataset.fullText = el.textContent;
                el.textContent = '';
                if (!prefersReducedMotion && typeof gsap !== 'undefined' && typeof ScrollTrigger !== 'undefined') {
                    ScrollTrigger.create({
                        trigger: el.closest('.timeline-row') || el,
                        start: 'center center+=40',
                        once: true,
                        onEnter: () => runTypewriter(el)
                    });
                } else if ('IntersectionObserver' in window) {
                    const io = new IntersectionObserver((entries) => {
                        entries.forEach(entry => {
                            if (entry.isIntersecting) {
                                runTypewriter(el);
                                io.unobserve(entry.target);
                            }
                        });
                    }, { threshold: 0.5 });
                    io.observe(el);
                } else {
                    el.textContent = el.dataset.fullText;
                }
            });
        }

        /* 图片灯箱 Lightbox */
        const lightboxEl = document.getElementById('lightbox');
        const lightboxImg = document.getElementById('lightbox-image');
        const lightboxCaption = document.getElementById('lightbox-caption');
        const lightboxMeta = document.getElementById('lightbox-meta');
        const lightboxCloseBtn = lightboxEl.querySelector('.lightbox__close');
        const lightboxPrev = lightboxEl.querySelector('.lightbox__nav--prev');
        const lightboxNext = lightboxEl.querySelector('.lightbox__nav--next');
        let lightboxItems = [];
        let lightboxIndex = 0;

        function buildLightboxItems(root) {
            const scope = root || document;
            const images = scope.querySelectorAll('.photo-frame img:not([data-lightbox-bound])');
            images.forEach(img => {
                img.dataset.lightboxBound = '1';
                const row = img.closest('.timeline-row');
                const captionEl = row ? row.querySelector('.photo-caption') : null;
                const { dateText, timeText } = getRowTimestamp(row);
                const timeLabel = (dateText || timeText) ? `${dateText} ${timeText}`.trim() : '';
                const fallbackTime = row ? (row.querySelector('.time-label')?.textContent.trim() || '') : '';
                const item = {
                    src: img.getAttribute('src'),
                    caption: captionEl ? captionEl.textContent.trim() : '',
                    time: timeLabel || fallbackTime
                };
                const index = lightboxItems.length;
                lightboxItems.push(item);
                img.dataset.lightboxIndex = String(index);
                img.addEventListener('click', () => openLightbox(index));
            });
        }

        function openLightbox(index) {
            if (!lightboxEl || !lightboxItems.length) return;
            lightboxIndex = index;
            const item = lightboxItems[index];
            lightboxImg.src = item.src;
            lightboxCaption.textContent = item.caption;
            lightboxMeta.textContent = item.time;
            lightboxEl.classList.add('lightbox--visible');
            lightboxEl.setAttribute('aria-hidden', 'false');
            document.documentElement.classList.add('modal-open');
            if (lenisInstance) lenisInstance.stop();
        }

        function closeLightbox() {
            if (!lightboxEl) return;
            lightboxEl.classList.remove('lightbox--visible');
            lightboxEl.setAttribute('aria-hidden', 'true');
            document.documentElement.classList.remove('modal-open');
            if (lenisInstance) lenisInstance.start();
        }

        function showLightboxOffset(delta) {
            if (!lightboxItems.length) return;
            lightboxIndex = (lightboxIndex + delta + lightboxItems.length) % lightboxItems.length;
            openLightbox(lightboxIndex);
        }

        if (lightboxCloseBtn) lightboxCloseBtn.addEventListener('click', closeLightbox);
        if (lightboxPrev) lightboxPrev.addEventListener('click', () => showLightboxOffset(-1));
        if (lightboxNext) lightboxNext.addEventListener('click', () => showLightboxOffset(1));
        if (lightboxEl) {
            lightboxEl.addEventListener('click', (e) => {
                if (e.target === lightboxEl) closeLightbox();
            });
            document.addEventListener('keydown', (e) => {
                if (!lightboxEl.classList.contains('lightbox--visible')) return;
                if (e.key === 'Escape') closeLightbox();
                if (e.key === 'ArrowLeft') showLightboxOffset(-1);
                if (e.key === 'ArrowRight') showLightboxOffset(1);
            });
        }

        /* GSAP 基础初始化 */
        if (!prefersReducedMotion && typeof gsap !== 'undefined' && typeof ScrollTrigger !== 'undefined') {
            gsap.registerPlugin(ScrollTrigger);
            if (lenisInstance) {
                lenisInstance.on('scroll', ScrollTrigger.update);
                ScrollTrigger.scrollerProxy(document.body, {
                    scrollTop(value) {
                        return arguments.length ? lenisInstance.scrollTo(value) : window.scrollY || window.pageYOffset;
                    },
                    getBoundingClientRect() {
                        return { top: 0, left: 0, width: window.innerWidth, height: window.innerHeight };
                    }
                });
            }
            enhanceTimelineRows(document);
            ScrollTrigger.addEventListener('refresh', () => {
                if (lenisInstance && typeof lenisInstance.update === 'function') lenisInstance.update();
            });
            ScrollTrigger.refresh();
        } else {
            document.querySelectorAll('.time-wrapper, .content-wrapper').forEach(el => {
                el.style.opacity = 1;
                el.style.transform = 'none';
            });
            initTypewriter(document);
        }

        buildLightboxItems(document);

        /* 无限加载 */
        let currentPage = Number(props.currentPage || 1);
        let loadingMore = false;
        let hasMore = !!props.hasMore;

        const sentinel = document.getElementById('scroll-sentinel');

        async function loadNextPage() {
            if (!hasMore || loadingMore) return;
            loadingMore = true;
            try {
                const params = new URLSearchParams(window.location.search);
                const nextPage = currentPage + 1;
                params.set('page', nextPage);
                const res = await fetch(`/api/timeline?${params.toString()}`, {
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                });
                if (!res.ok) return;
                const data = await res.json();
                if (data.html) {
                    const temp = document.createElement('div');
                    temp.innerHTML = data.html;
                    const newRows = temp.querySelectorAll('.timeline-row');
                    const grid = document.querySelector('.timeline-grid');
                    newRows.forEach((row) => grid.appendChild(row));

                    bindEditButtons(temp);
                    initMagneticElements(temp);
                    enhanceTimelineRows(temp);
                    bindTimelineHover(temp);    // ★ 给新加载的行绑定 hover
                    buildLightboxItems(temp);

                    if (typeof ScrollTrigger !== 'undefined') ScrollTrigger.refresh();
                }
                currentPage = nextPage;
                hasMore = !!data.has_more;
                if (!hasMore && sentinel) sentinel.remove();
            } catch (e) {
                console.error(e);
            } finally {
                loadingMore = false;
            }
        }

        if (sentinel && hasMore && 'IntersectionObserver' in window) {
            const ioMore = new IntersectionObserver((entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) loadNextPage();
                });
            }, { rootMargin: '0px 0px 300px 0px' });
            ioMore.observe(sentinel);
        }
}


function initAnniversariesPage(props) {
    const prefersReducedMotion =
            window.matchMedia &&
            window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        let lenisInstance = null;

        const cursorGlow = document.getElementById('cursor-glow');
        let mouseX = window.innerWidth / 2;
        let mouseY = window.innerHeight / 2;
        let currentX = mouseX;
        let currentY = mouseY;

        if (cursorGlow) {
            document.addEventListener('mousemove', (e) => {
                mouseX = e.clientX;
                mouseY = e.clientY;
            });

            (function animateCursor() {
                currentX += (mouseX - currentX) * 0.12;
                currentY += (mouseY - currentY) * 0.12;
                cursorGlow.style.left = currentX + 'px';
                cursorGlow.style.top = currentY + 'px';
                if (!prefersReducedMotion) requestAnimationFrame(animateCursor);
            })();
        }

        const canvas = document.getElementById('hearts-canvas');
        const ctx = canvas.getContext('2d');
        let hearts = [];
        let isAnimatingHearts = false;

        function resizeCanvas() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }
        window.addEventListener('resize', resizeCanvas);
        resizeCanvas();

        function triggerHearts() {
            const originX = window.innerWidth / 2;
            const originY = window.innerHeight - 80;

            for (let i = 0; i < 26; i++) {
                hearts.push({
                    x: originX,
                    y: originY,
                    size: Math.random() * 20 + 6,
                    speedX: (Math.random() - 0.5) * 12,
                    speedY: Math.random() * -15 - 6,
                    opacity: 1,
                    rotation: Math.random() * 360
                });
            }

            if (!isAnimatingHearts) {
                isAnimatingHearts = true;
                animateHearts();
            }
        }
        window.triggerHearts = triggerHearts;

        function animateHearts() {
            if (hearts.length === 0) {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                isAnimatingHearts = false;
                return;
            }
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            hearts.forEach((h, i) => {
                h.x += h.speedX;
                h.y += h.speedY;
                h.speedY += 0.35;
                h.opacity -= 0.012;

                ctx.save();
                ctx.translate(h.x, h.y);
                ctx.rotate(h.rotation);
                ctx.fillStyle = 'rgba(255,0,60,' + h.opacity + ')';
                ctx.font = h.size + 'px serif';
                ctx.fillText('❤', -h.size / 2, h.size / 2);
                ctx.restore();

                if (h.opacity <= 0) hearts.splice(i, 1);
            });
            requestAnimationFrame(animateHearts);
        }

        const modal = document.getElementById('input-modal');
        const backdrop = document.getElementById('modal-backdrop');
        const dateInput = document.getElementById('date-input');
        const form = document.getElementById('modal-form');

        function syncNowToDateInput() {
            if (!dateInput) return;
            const now = new Date();
            now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
            dateInput.value = now.toISOString().slice(0, 16);
        }

        function openModal() {
            syncNowToDateInput();
            document.documentElement.classList.add('modal-open');
            if (lenisInstance) lenisInstance.stop();
            backdrop.classList.add('active');
            modal.showModal();

            const hidden = document.getElementById('kd-hidden');
            if (hidden && dateInput) hidden.value = dateInput.value;
        }
        function closeModal() {
            backdrop.classList.remove('active');
            modal.close();
            document.documentElement.classList.remove('modal-open');
            if (lenisInstance) lenisInstance.start();
        }
        window.openModal = openModal;
        window.closeModal = closeModal;
        backdrop.addEventListener('click', closeModal);

        form.onsubmit = function () {
            const hidden = document.getElementById('kd-hidden');
            if (hidden && dateInput) hidden.value = dateInput.value;
            form.action = "props.addKeydateUrl || '/add/keydate'";
        };

        if (!prefersReducedMotion && typeof Lenis !== 'undefined') {
            const lenis = new Lenis({
                lerp: 0.12,
                smoothWheel: true,
                smoothTouch: false,
                wheelMultiplier: 1.1
            });
            lenisInstance = lenis;

            function raf(time) {
                lenis.raf(time);
                requestAnimationFrame(raf);
            }
            requestAnimationFrame(raf);
        }

        if (!prefersReducedMotion && typeof gsap !== 'undefined') {
            const cards = document.querySelectorAll('.anniv-card');
            cards.forEach((card, index) => {
                gsap.fromTo(card,
                    { opacity: 0, y: 40 },
                    {
                        opacity: 1,
                        y: 0,
                        duration: 0.7,
                        delay: index * 0.05,
                        ease: 'power3.out'
                    }
                );
            });
        } else {
            document.querySelectorAll('.anniv-card').forEach(c => {
                c.style.opacity = 1;
                c.style.transform = 'none';
            });
        }

        function initMagneticElements() {
            if (typeof gsap === 'undefined') return;
            const magneticItems = document.querySelectorAll('[data-magnetic]');
            magneticItems.forEach((item) => {
                const strength = parseFloat(item.dataset.magneticStrength || '0.25');
                let bounds;
                function onMouseMove(e) {
                    if (!bounds) bounds = item.getBoundingClientRect();
                    const relX = e.clientX - (bounds.left + bounds.width / 2);
                    const relY = e.clientY - (bounds.top + bounds.height / 2);
                    gsap.to(item, {
                        x: relX * strength,
                        y: relY * strength,
                        duration: 0.5,
                        ease: 'power3.out'
                    });
                }
                function reset() {
                    bounds = null;
                    gsap.to(item, {
                        x: 0,
                        y: 0,
                        duration: 0.8,
                        ease: 'elastic.out(1.1, 0.4)'
                    });
                }
                item.addEventListener('mouseenter', () => {
                    bounds = item.getBoundingClientRect();
                    window.addEventListener('mousemove', onMouseMove);
                    if (cursorGlow) cursorGlow.classList.add('cursor-glow--active');
                });
                item.addEventListener('mouseleave', () => {
                    window.removeEventListener('mousemove', onMouseMove);
                    reset();
                    if (cursorGlow) cursorGlow.classList.remove('cursor-glow--active');
                });
            });
        }
        initMagneticElements();
}


function initMapPage(props) {
    const markersData = props.markers || [];

        const map = new AMap.Map('map', {
            viewMode: '2D',
            zoom: 4,
            center: [104.06, 30.67],
            mapStyle: 'amap://styles/dark',
            pitch: 0,
            dragEnable: true,
            zoomEnable: true,
        });

        const validMarkers = markersData.filter(m => m.lat !== null && m.lng !== null);
        let markerInstances = [];
        let currentInfoWindow = null;
        let geocoder = null;
        const visitedAdcodes = new Set();
        const provincePolygons = new Map();
        const provinceFeatures = new Map(); // adcode -> array of features
        let geojsonLoaded = false;
        let geojsonPromise = null;
        const normalizeAdcode = (code) => {
            if (!code) return null;
            const s = String(code).padEnd(6, '0').slice(0, 6);
            // 省级编码：前两位 + 0000
            return s.slice(0, 2) + '0000';
        };
        function loadGeoJSON() {
            if (geojsonLoaded) return Promise.resolve(provinceFeatures);
            if (geojsonPromise) return geojsonPromise;
            geojsonPromise = fetch('/static/geo/china-provinces.geojson')
                .then(r => r.json())
                .then(data => {
                    (data.features || []).forEach(f => {
                        const props = f.properties || {};
                        const code = normalizeAdcode(props.adcode || props.parent?.adcode || (props.acroutes || []).slice(-1)[0]);
                        if (!code) return;
                        if (!provinceFeatures.has(code)) provinceFeatures.set(code, []);
                        provinceFeatures.get(code).push(f);
                    });
                    geojsonLoaded = true;
                    console.log('[Map] GeoJSON loaded, provinces:', provinceFeatures.size);
                    return provinceFeatures;
                })
                .catch(err => {
                    console.log('[Map] Load geojson failed', err);
                    geojsonLoaded = false;
                });
            return geojsonPromise;
        }
        const fallbackAdcode = (lat, lng) => {
            // 手动兜底的省级范围：青海、上海、浙江、北京、吉林、河南、江苏
            if (lat > 35 && lat < 37 && lng > 100 && lng < 102) return '630000'; // Qinghai (Xining)
            if (lat > 30 && lat < 32.2 && lng > 120 && lng < 122.5) return '310000'; // Shanghai
            if (lat > 27 && lat < 31.8 && lng > 118 && lng < 123) return '330000'; // Zhejiang
            if (lat > 39 && lat < 41.2 && lng > 115 && lng < 117.5) return '110000'; // Beijing
            if (lat > 41 && lat < 45 && lng > 123 && lng < 129) return '220000'; // Jilin
            if (lat > 33 && lat < 36 && lng > 110 && lng < 116) return '410000'; // Henan
            if (lat > 31 && lat < 35.5 && lng > 116 && lng < 122) return '320000'; // Jiangsu
            return null;
        };

        const filterState = {
            entry: true,
            photo: true,
            keydate: true
        };

        function colorForKind(kind) {
            if (kind === 'photo') return 'rgba(140,170,255,0.9)';
            if (kind === 'keydate') return '#ff003c';
            return 'rgba(255,255,255,0.9)';
        }

        const positionCounts = {};

        function getJitteredPos(lat, lng) {
            const key = Math.round(lat * 10) + ',' + Math.round(lng * 10);
            if (!positionCounts[key]) positionCounts[key] = 0;
            const count = positionCounts[key];
            positionCounts[key]++;

            if (count > 0) {
                const angle = count * 137.5 * (Math.PI / 180);
                const radius = 0.012 * Math.sqrt(count);
                const newLat = lat + radius * Math.cos(angle);
                const newLng = lng + radius * Math.sin(angle) * 1.3;
                return new AMap.LngLat(newLng, newLat);
            }
            return new AMap.LngLat(lng, lat);
        }

        function formatGeoLabel(originalLabel, lat, lng) {
            let text = originalLabel || '';
            text = text.replace(/^[\d\.\-,]+\s*/, '');
            const latNum = parseFloat(lat);
            const lngNum = parseFloat(lng);
            if (isNaN(latNum) || isNaN(lngNum)) return text;
            const latInt = Math.floor(latNum);
            const lngInt = Math.floor(lngNum);
            const coordsStr = `${latInt} ${lngInt}`;
            if (text) {
                return `${coordsStr} ${text}`;
            }
            return coordsStr;
        }

        function buildMarker(m) {
            const color = colorForKind(m.kind);
            const pos = getJitteredPos(m.lat, m.lng);

            let marker;
            if (m.kind === 'keydate') {
                marker = new AMap.Marker({
                    position: pos,
                    anchor: 'center',
                    offset: new AMap.Pixel(0, 0),
                    zIndex: 300,
                    content: '<div class="keydate-pin"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21s-7-4.35-9.33-9.27C1.2 9.08 2.5 5.5 5.73 4.6c1.9-.52 3.61.22 4.77 1.7 1.16-1.48 2.87-2.22 4.77-1.7 3.23.89 4.53 4.48 3.06 7.13C19 16.65 12 21 12 21Z"/></svg></div>',
                    bubble: true,
                    extData: { kind: m.kind }
                });
            } else {
                marker = new AMap.CircleMarker({
                    center: pos,
                    radius: 3.6,
                    strokeColor: 'rgba(0,0,0,0.4)',
                    strokeWeight: 0.6,
                    fillColor: color,
                    fillOpacity: 0.85,
                    zIndex: 80,
                    cursor: 'pointer',
                    bubble: true,
                    extData: { kind: m.kind }
                });
            }

            const displayGeo = formatGeoLabel(m.label, m.lat, m.lng);

            let contentHtml = '';
            if (m.image) {
                contentHtml += `<img src="${m.image}" class="info-img" loading="lazy">`;
            }
            let snippet = m.snippet || '';
            if (snippet.length > 60) snippet = snippet.substring(0, 60) + '...';

            contentHtml += `<div class="info-content">${snippet}</div>`;

            const html = `
                <div class="amap-info-window-custom">
                    <span class="info-close" onclick="closeInfoWindow()">×</span>
                    <div class="info-time">${m.timestamp}</div>
                    ${contentHtml}
                    <div class="info-geo">${displayGeo}</div>
                </div>
            `;

            marker.on('click', () => {
                if (currentInfoWindow) currentInfoWindow.close();
                const info = new AMap.InfoWindow({
                    isCustom: true,
                    content: html,
                    offset: new AMap.Pixel(0, -12),
                    autoMove: true
                });
                info.open(map, pos);
                currentInfoWindow = info;
            });

            marker.setMap(map);
            markerInstances.push(marker);
        }

        window.closeInfoWindow = function() {
            if (currentInfoWindow) {
                currentInfoWindow.close();
                currentInfoWindow = null;
            }
        };

        window.toggleFilter = function(type) {
            filterState[type] = !filterState[type];
            const el = document.getElementById('filter-' + type);
            if (filterState[type]) {
                el.classList.remove('is-off');
            } else {
                el.classList.add('is-off');
            }
            markerInstances.forEach(marker => {
                const k = marker.getExtData().kind;
                if (filterState[k]) {
                    marker.show();
                } else {
                    marker.hide();
                }
            });
        };

        // 【修复重点】使用 setZoom 配合 duration 实现平滑缩放
        window.zoomIn = function() {
            map.setZoom(map.getZoom() + 1, false, 400);
        };

        window.zoomOut = function() {
            map.setZoom(map.getZoom() - 1, false, 400);
        };

        function drawProvince(adcode) {
            if (provincePolygons.has(adcode)) return;
            const feats = provinceFeatures.get(adcode);
            if (!feats || !feats.length) return;
            const fill = 'rgba(255,0,60,0.12)';
            const polys = [];
            feats.forEach(f => {
                const geom = f.geometry || {};
                const type = geom.type;
                const coords = geom.coordinates || [];
                if (type === 'MultiPolygon') {
                    coords.forEach(poly => {
                        const paths = poly.map(ring => ring.map(([lng, lat]) => [lng, lat]));
                        if (paths.length) {
                            const p = new AMap.Polygon({
                                path: paths,
                                fillColor: '#ff003c',
                                fillOpacity: 0.42,
                                strokeColor: '#ff003c',
                                strokeOpacity: 0.65,
                                strokeWeight: 1,
                                zIndex: 5,
                                bubble: false
                            });
                            p.setMap(map);
                            polys.push(p);
                        }
                    });
                } else if (type === 'Polygon') {
                    const paths = coords.map(ring => ring.map(([lng, lat]) => [lng, lat]));
                    if (paths.length) {
                        const p = new AMap.Polygon({
                            path: paths,
                            fillColor: '#ff003c',
                            fillOpacity: 0.42,
                            strokeColor: '#ff003c',
                            strokeOpacity: 0.65,
                            strokeWeight: 1,
                            zIndex: 5,
                            bubble: false
                        });
                        p.setMap(map);
                        polys.push(p);
                    }
                }
            });
            if (polys.length) {
                provincePolygons.set(adcode, polys);
            }
        }

        function refreshProvincePolygons() {
            if (!geojsonLoaded) {
                loadGeoJSON().then(refreshProvincePolygons);
                return;
            }
            visitedAdcodes.forEach(code => drawProvince(code));
            console.log('[Map] Provinces drawn:', Array.from(provincePolygons.keys()));
        }

        function resolveVisitedAdcodes() {
            if (!geocoder) return;
            const uniquePoints = {};
            validMarkers.forEach(m => {
                const key = `${m.lat.toFixed(2)},${m.lng.toFixed(2)}`;
                if (!uniquePoints[key]) {
                    uniquePoints[key] = { lat: m.lat, lng: m.lng };
                }
            });

            Object.values(uniquePoints).forEach(pt => {
                const fbEarly = fallbackAdcode(pt.lat, pt.lng);
                if (fbEarly) {
                    visitedAdcodes.add(fbEarly);
                }
                geocoder.getAddress([pt.lng, pt.lat], (status, result) => {
                    if (status === 'complete' && result.regeocode) {
                        const raw = result.regeocode.addressComponent?.adcode;
                        const code = normalizeAdcode(raw);
                        console.log('[Map] Geocode success', { lat: pt.lat, lng: pt.lng, rawAdcode: raw, normalized: code });
                        if (code) {
                            visitedAdcodes.add(code);
                        }
                    } else {
                        console.log('[Map] Geocode failed', { lat: pt.lat, lng: pt.lng, status, result });
                    }
                    const fb = fallbackAdcode(pt.lat, pt.lng);
                    if (fb) {
                        console.log('[Map] Fallback adcode', fb, 'for', pt);
                        visitedAdcodes.add(fb);
                    }
                    refreshProvincePolygons();
                });
            });
        }

        validMarkers.forEach(m => buildMarker(m));

        map.plugin(['AMap.Geocoder'], function () {
            geocoder = new AMap.Geocoder({ extensions: 'all' });
            loadGeoJSON().then(resolveVisitedAdcodes);
        });

        if (markerInstances.length > 0) {
            map.setFitView(null, false, [100, 60, 100, 60]);
        }
}



function waitForAMap(cb, retries=30) {
    if (window.AMap) { cb(); return; }
    if (retries <= 0) return;
    setTimeout(() => waitForAMap(cb, retries - 1), 200);
}



document.addEventListener('DOMContentLoaded', () => {
    const props = window.PAGE_PROPS || {};
    if (typeof initBasePage === 'function') initBasePage();
    const page = props.pageId || document.body.dataset.page || '';
    if (page === 'index') {
        if (typeof initIndexPage === 'function') initIndexPage(props);
    } else if (page === 'anniversaries') {
        if (typeof initAnniversariesPage === 'function') initAnniversariesPage(props);
    } else if (page === 'map') {
        waitForAMap(() => {
            if (typeof initMapPage === 'function') initMapPage(props);
        });
    }
});

})();
