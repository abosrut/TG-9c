document.addEventListener('DOMContentLoaded', function() {
    const tg = window.Telegram.WebApp;
    tg.expand();

    const tabsContainer = document.querySelector('.tabs');
    const contentContainer = document.querySelector('.schedule-content');
    const searchBox = document.getElementById('search-box');
    
    let fullScheduleData = {};
    let currentDayIndex = 0;
    let touchStartX = 0;
    let touchEndX = 0;

    const days = [
        { short: 'Пн', full: 'Понедельник' },
        { short: 'Вт', full: 'Вторник' },
        { short: 'Ср', full: 'Среда' },
        { short: 'Чт', full: 'Четверг' },
        { short: 'Пт', full: 'Пятница' },
    ];
    
    function showDay(dayIndex) {
        currentDayIndex = dayIndex;
        const dayShort = days[dayIndex].short;
        
        document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
        document.querySelectorAll('.day-schedule').forEach(div => div.style.display = 'none');

        const activeButton = document.querySelector(`.tab-button[data-day="${dayShort}"]`);
        const activeSchedule = document.getElementById(`schedule-${dayShort}`);
        
        if (activeButton) activeButton.classList.add('active');
        if (activeSchedule) activeSchedule.style.display = 'block';
        
        filterSchedule();
    }
    
    function filterSchedule() {
        const query = searchBox.value.toLowerCase();
        
        document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('highlight'));

        days.forEach(day => {
            const dayShort = day.short;
            const scheduleDiv = document.getElementById(`schedule-${dayShort}`);
            if (!scheduleDiv) return;
            
            let dayHasMatch = false;
            scheduleDiv.querySelectorAll('.lesson-item').forEach(item => {
                const subject = item.dataset.subject.toLowerCase();
                if (subject.includes(query)) {
                    item.classList.remove('hidden');
                    dayHasMatch = true;
                } else {
                    item.classList.add('hidden');
                }
            });

            if (dayHasMatch && query) {
                document.querySelector(`.tab-button[data-day="${dayShort}"]`).classList.add('highlight');
            }
        });
    }

    async function loadSchedule() {
        try {
            const response = await fetch('/api/schedule');
            fullScheduleData = await response.json();
            renderSchedule(fullScheduleData);
        } catch (error) {
            contentContainer.innerHTML = '<p>Не удалось загрузить расписание.</p>';
        }
    }

    function renderSchedule(data) {
        tabsContainer.innerHTML = '';
        contentContainer.innerHTML = '';

        days.forEach((day, index) => {
            const dayShort = day.short;
            const lessons = data[dayShort] || [];

            const tabButton = document.createElement('button');
            tabButton.className = 'tab-button';
            tabButton.dataset.day = dayShort;
            tabButton.textContent = dayShort;
            tabButton.onclick = () => showDay(index);
            tabsContainer.appendChild(tabButton);

            const scheduleDiv = document.createElement('div');
            scheduleDiv.className = 'day-schedule';
            scheduleDiv.id = `schedule-${dayShort}`;
            
            if (lessons.length > 0) {
                lessons.forEach(lesson => {
                    const item = document.createElement('div');
                    item.className = 'lesson-item';
                    item.dataset.subject = lesson.subject;
                    item.innerHTML = `
                        <div class="lesson-number">${lesson.number}</div>
                        <div class="lesson-details">
                            <div class="lesson-subject">${lesson.subject}</div>
                            <div class="lesson-time">${lesson.time}</div>
                        </div>
                    `;
                    scheduleDiv.appendChild(item);
                });
            } else {
                scheduleDiv.innerHTML = '<p style="text-align: center; margin-top: 20px;">🎉 Уроков нет!</p>';
            }
            contentContainer.appendChild(scheduleDiv);
        });

        let initialDayIndex = new Date().getDay() - 1; 
        if (initialDayIndex < 0 || initialDayIndex > 4) initialDayIndex = 0;
        showDay(initialDayIndex);
    }
    
    function handleTouchStart(e) { touchStartX = e.changedTouches[0].screenX; }
    function handleTouchEnd(e) {
        touchEndX = e.changedTouches[0].screenX;
        handleSwipe();
    }
    function handleSwipe() {
        const swipeThreshold = 50;
        if (touchEndX < touchStartX - swipeThreshold) {
            if (currentDayIndex < days.length - 1) showDay(currentDayIndex + 1);
        }
        if (touchEndX > touchStartX + swipeThreshold) {
            if (currentDayIndex > 0) showDay(currentDayIndex - 1);
        }
    }
    
    searchBox.addEventListener('input', filterSchedule);
    contentContainer.addEventListener('touchstart', handleTouchStart, false);
    contentContainer.addEventListener('touchend', handleTouchEnd, false);

    loadSchedule();
});