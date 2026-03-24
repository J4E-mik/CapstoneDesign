let chart;
let currentPreference = null;

document.querySelectorAll('.prefBtn').forEach(btn => {
    btn.addEventListener('click', function () {
        document.querySelectorAll('.prefBtn').forEach(b => b.classList.remove('selected'));
        this.classList.add('selected');
        currentPreference = this.dataset.pref;
        const userId = document.getElementById("user_id").value.trim();
        if (userId) fetchAndDraw(userId, currentPreference);
    });
});

document.getElementById("loadBtn").addEventListener("click", () => {
    const userId = document.getElementById("user_id").value.trim();
    if (!userId) {
        document.getElementById("error").innerText = "User ID를 입력하세요!";
        return;
    }
    document.getElementById("error").innerText = "";
    fetchAndDraw(userId, currentPreference);
});

function fetchAndDraw(userId, preference) {
    // preference가 null이면, 쿼리에서 아예 파라미터를 빼거나 'all'로 넘김
    let url = `/nav/scores?user_id=${encodeURIComponent(userId)}`;
    if (preference) {
        url += `&preference=${preference}`;
    } else {
        url += `&preference=all`; // 백엔드에서 all은 모두 1.0로 처리
    }
    fetch(url)
        .then(res => {
            if (!res.ok) throw new Error("API 에러");
            return res.json();
        })
        .then(data => {
            drawChart(data);
        })
        .catch(err => {
            document.getElementById("error").innerText = err.message;
            if (chart) chart.destroy();
        });
}


function drawChart(data) {
    const ctx = document.getElementById("routeScoreChart").getContext("2d");
    const labels = data.map(d => `경로 ${d.index + 1}`);
    const walk = data.map(d => d.walk_score);
    const bus = data.map(d => d.bus_score);
    const subway = data.map(d => d.subway_score);
    const totals = data.map(d => d.total_score);

    // 최저점(가장 좋은 경로)과 최고점(가장 나쁜 경로)
    const minScore = Math.min(...totals);
    const maxScore = Math.max(...totals);

    // Subway(맨 위 stack)에만 하이라이트 컬러 적용
    const highlightGood = '#7ed957'; // 연두
    const highlightBad = '#ffc97e';  // 주황
    const defaultSubway = '#43aa8b'; // 일반 subway 컬러

    const subwayColors = subway.map((v, i) =>
        totals[i] === minScore ? highlightGood :
        totals[i] === maxScore ? highlightBad : defaultSubway
    );

    if (chart) chart.destroy(); // 기존 차트 삭제

    chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                { label: 'Walk', data: walk, backgroundColor: '#ffba08' },
                { label: 'Bus', data: bus, backgroundColor: '#577590' },
                { label: 'Subway', data: subway, backgroundColor: subwayColors }
            ]
        },
        options: {
            plugins: {
                title: {
                    display: true,
                    text: '경로별 점수(Breakdown)',
                    font: { size: 22 }
                },
                legend: { position: 'top' },
                tooltip: { mode: 'index', intersect: false },
                datalabels: {
                    anchor: 'end',
                    align: 'end',
                    formatter: function(value, context) {
                        // subway dataset(맨 위 stack)에만 종합점수 표시
                        if (context.datasetIndex === 2) {
                            return totals[context.dataIndex].toFixed(1);
                        }
                        return '';
                    },
                    font: { weight: 'bold', size: 14 },
                    color: function(context) {
                        const idx = context.dataIndex;
                        if (totals[idx] === minScore) return highlightGood;
                        if (totals[idx] === maxScore) return highlightBad;
                        return '#212a3e';
                    }
                }
            },
            responsive: true,
            scales: {
                x: { stacked: true },
                y: {
                    stacked: true,
                    title: { display: true, text: 'Score (낮을수록 우수)' }
                }
            }
        },
        plugins: [ChartDataLabels]
    });
}