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
                        t.innerText = tile.number;
                        h.appendChild(t);
                    }
                    row.appendChild(h);
                }
                board.appendChild(row);
            });
        });
}
window.onload = generate;
