function getPips(num) {
    // Catan probability: number of ways to roll the value with 2d6
    const pipCount = {
        2: 1, 12: 1,
        3: 2, 11: 2,
        4: 3, 10: 3,
        5: 4, 9: 4,
        6: 5, 8: 5
    };
    return ".".repeat(pipCount[num] || 0);
}

function generate() {
    const isExp = document.querySelector('input[name="mode"]:checked').value === 'exp';
    const query = new URLSearchParams({
        expansion: isExp,
        no_adj_res: document.getElementById('res').checked,
        no_adj_red: document.getElementById('red').checked,
        no_same_nums: document.getElementById('same').checked,
        center_desert: document.getElementById('center').checked
    });

    fetch(`/generate?${query}`)
        .then(r => r.json())
        .then(data => {
            if (data.error) return alert(data.error);
            const board = document.getElementById('board');
            board.innerHTML = '';
            const rows = isExp ? [3,4,5,6,5,4,3] : [3,4,5,4,3];
            let i = 0;
            rows.forEach(count => {
                const row = document.createElement('div');
                row.className = 'row';
                for(let j=0; j<count; j++) {
                    const tile = data[i++];
                    const h = document.createElement('div');
                    h.className = `hex ${tile.resource}`;
                    
                    if(tile.number) {
                        const t = document.createElement('div');
                        t.className = `token ${[6,8].includes(tile.number) ? 'red' : ''}`;
                        
                        // Create Number Span
                        const nSpan = document.createElement('span');
                        nSpan.innerText = tile.number;
                        
                        // Create Pips Div
                        const pDiv = document.createElement('div');
                        pDiv.className = 'pips';
                        pDiv.innerText = getPips(tile.number);
                        
                        t.appendChild(nSpan);
                        t.appendChild(pDiv);
                        h.appendChild(t);
                    }
                    row.appendChild(h);
                }
                board.appendChild(row);
            });
        });
}
window.onload = generate;
