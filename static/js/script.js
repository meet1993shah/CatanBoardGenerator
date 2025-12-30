function generate() {
    const isExp = document.querySelector('input[name="mode"]:checked').value === 'exp';
    const params = new URLSearchParams({
        expansion: isExp,
        no_adj_res: document.getElementById('res').checked,
        no_adj_red: document.getElementById('red').checked,
        no_same_nums: document.getElementById('same').checked,
        center_desert: document.getElementById('center').checked
    });

    fetch(`/generate?${params}`)
        .then(res => res.json())
        .then(data => {
            if(data.error) return alert(data.error);
            const board = document.getElementById('board');
            board.innerHTML = '';
            const layout = isExp ? [3,4,5,6,5,4,3] : [3,4,5,4,3];
            let idx = 0;
            layout.forEach(count => {
                const row = document.createElement('div');
                row.className = 'row';
                for(let i=0; i<count; i++) {
                    const tile = data[idx++];
                    const h = document.createElement('div');
                    h.className = `hex ${tile.resource}`;
                    if(tile.number) {
                        const n = document.createElement('div');
                        n.className = `num ${[6,8].includes(tile.number) ? 'red' : ''}`;
                        n.innerText = tile.number;
                        h.appendChild(n);
                    }
                    row.appendChild(h);
                }
                board.appendChild(row);
            });
        });
}
window.onload = generate;
