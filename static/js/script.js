const genBtn = document.getElementById('gen-btn');
const boardDiv = document.getElementById('board');

function getPips(n) {
    const pips = {2:1, 12:1, 3:2, 11:2, 4:3, 10:3, 5:4, 9:4, 6:5, 8:5};
    return ".".repeat(pips[n] || 0);
}

function fetchBoard() {
    const isExp = document.querySelector('input[name="mode"]:checked').value === 'exp';
    const params = new URLSearchParams({
        expansion: isExp,
        no_adj_res: document.getElementById('no-adj-res').checked,
        no_adj_red: document.getElementById('no-adj-red').checked,
        no_same_nums: document.getElementById('no-same-nums').checked
    });

    fetch(`/generate?${params}`)
        .then(res => res.json())
        .then(data => render(data, isExp));
}

function render(data, isExp) {
    boardDiv.innerHTML = '';
    const layout = isExp ? [3, 4, 5, 6, 5, 4, 3] : [3, 4, 5, 4, 3];
    let idx = 0;

    layout.forEach(count => {
        const row = document.createElement('div');
        row.className = 'row';
        for (let i = 0; i < count; i++) {
            const tile = data[idx++];
            if(!tile) break;
            const hex = document.createElement('div');
            hex.className = `hex ${tile.resource}`;
            
            if (tile.number) {
                const circle = document.createElement('div');
                circle.className = `num-circle ${[6,8].includes(tile.number) ? 'red-num' : ''}`;
                circle.innerHTML = `<span>${tile.number}</span><div class="pips">${getPips(tile.number)}</div>`;
                hex.appendChild(circle);
            }
            row.appendChild(hex);
        }
        boardDiv.appendChild(row);
    });
}

genBtn.addEventListener('click', fetchBoard);
window.onload = fetchBoard;
