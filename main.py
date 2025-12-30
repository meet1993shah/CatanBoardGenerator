from flask import Flask, render_template, jsonify, request
import random

app = Flask(__name__)

# Data Sets
BASE_RES = (['forest']*4 + ['hills']*3 + ['mountains']*3 + ['fields']*4 + ['pasture']*4 + ['desert']*1)
EXP_RES = (['forest']*6 + ['hills']*5 + ['mountains']*5 + ['fields']*6 + ['pasture']*6 + ['desert']*2)
BASE_NUMS = [2, 12, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11]
EXP_NUMS = [2, 2, 12, 12, 3, 3, 3, 4, 4, 4, 5, 5, 5, 6, 6, 6, 8, 8, 8, 9, 9, 9, 10, 10, 10, 11, 11, 11]

def get_grid_neighbors(is_exp):
    """Generates an adjacency list based on the Catan grid layout."""
    layout = [3, 4, 5, 6, 5, 4, 3] if is_exp else [3, 4, 5, 4, 3]
    neighbors = {}
    
    # Convert index to (row, col)
    idx_to_coord = {}
    curr = 0
    for r, count in enumerate(layout):
        for c in range(count):
            idx_to_coord[curr] = (r, c)
            curr += 1
            
    # Calculate neighbors based on staggered row offset
    for i, (r, c) in idx_to_coord.items():
        neighbors[i] = []
        # Row-based offsets for hexagonal adjacency
        # This varies if the row length is increasing or decreasing
        for ni, (nr, nc) in idx_to_coord.items():
            if i == ni: continue
            # Basic distance check for adjacent hexes
            row_diff = abs(r - nr)
            col_diff = abs(c - nc)
            if row_diff == 0 and col_diff == 1: # Same row
                neighbors[i].append(ni)
            elif row_diff == 1: # Adjacent row
                # Logic for staggered hex alignment
                len_curr = layout[r]
                len_next = layout[nr]
                if len_next > len_curr: # Moving toward middle
                    if nc == c or nc == c + 1: neighbors[i].append(ni)
                elif len_next < len_curr: # Moving away from middle
                    if nc == c or nc == c - 1: neighbors[i].append(ni)
                else: # Same length (only happens in expansion)
                    if nc == c or nc == c + (1 if nr > r else -1): # Simplified
                         pass 
    return neighbors

# Hardcoded neighbors for precision (Base 19)
NEIGHBORS_19 = {
    0:[1,3,4], 1:[0,2,4,5], 2:[1,5,6], 3:[0,4,7,8], 4:[0,1,3,5,8,9], 5:[1,2,4,6,9,10],
    6:[2,5,10,11], 7:[3,8,12], 8:[3,4,7,9,12,13], 9:[4,5,8,10,13,14], 10:[5,6,9,11,14,15],
    11:[6,10,15], 12:[7,8,13,16], 13:[8,9,12,14,16,17], 14:[9,10,13,15,17,18], 15:[10,11,14,18],
    16:[12,13,17], 17:[13,14,16,18], 18:[14,15,17]
}

# Simplified for Expansion - In production, use a full map
NEIGHBORS_30 = get_grid_neighbors(True)

def validate(board, no_res, no_red, no_same, adj_map):
    for i, tile in enumerate(board):
        for neighbor in adj_map.get(i, []):
            if neighbor >= len(board): continue
            
            # 1. Resource Adjacency
            if no_res and tile['resource'] == board[neighbor]['resource']:
                return False
            
            v1, v2 = tile['number'], board[neighbor]['number']
            if v1 and v2:
                # 2. Red Adjacency (6 & 8)
                if no_red and v1 in [6,8] and v2 in [6,8]: return False
                # 3. Same Number Adjacency
                if no_same and v1 == v2: return False
    return True

@app.route('/')
def index(): return render_template('index.html')

@app.route('/generate')
def generate():
    is_exp = request.args.get('expansion') == 'true'
    no_res = request.args.get('no_adj_res') == 'true'
    no_red = request.args.get('no_adj_red') == 'true'
    no_same = request.args.get('no_same_nums') == 'true'
    center_desert = request.args.get('center_desert') == 'true'

    adj_map = NEIGHBORS_30 if is_exp else NEIGHBORS_19
    res_pool = EXP_RES[:] if is_exp else BASE_RES[:]
    num_pool = EXP_NUMS[:] if is_exp else BASE_NUMS[:]
    
    for _ in range(5000): # Increase iterations for strict rules
        random.shuffle(res_pool)
        if center_desert:
            d_idx = 14 if is_exp else 9
            if res_pool[d_idx] != 'desert':
                orig_idx = res_pool.index('desert')
                res_pool[d_idx], res_pool[orig_idx] = res_pool[orig_idx], res_pool[d_idx]

        random.shuffle(num_pool)
        board = []
        n_ptr = 0
        for r in res_pool:
            num = None
            if r != 'desert':
                num = num_pool[n_ptr]
                n_ptr += 1
            board.append({'resource': r, 'number': num})
        
        if validate(board, no_res, no_red, no_same, adj_map):
            return jsonify(board)

    return jsonify({"error": "Failed to find valid board. Try fewer constraints."}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5001)
