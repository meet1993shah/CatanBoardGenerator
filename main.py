from flask import Flask, render_template, jsonify, request
import random
import os
import platform

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Official Catan Component Pools
BASE_RES = (['forest']*4 + ['hills']*3 + ['mountains']*3 + ['fields']*4 + ['pasture']*4 + ['desert']*1)
EXP_RES = (['forest']*6 + ['hills']*5 + ['mountains']*5 + ['fields']*6 + ['pasture']*6 + ['desert']*2)
BASE_NUMS = [2, 12, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11]
EXP_NUMS = [2, 2, 12, 12, 3, 3, 3, 4, 4, 4, 5, 5, 5, 6, 6, 6, 8, 8, 8, 9, 9, 9, 10, 10, 10, 11, 11, 11]

def get_neighbors_map(layout):
    """Generates neighbor indices for any staggered hex grid layout."""
    neighbors = {}
    idx_to_coord = {}
    curr = 0
    for r, count in enumerate(layout):
        for c in range(count):
            idx_to_coord[curr] = (r, c)
            curr += 1
    
    for i, (r, c) in idx_to_coord.items():
        neighbors[i] = []
        for ni, (nr, nc) in idx_to_coord.items():
            if i == ni: continue
            dr, dc = nr - r, nc - c
            if abs(dr) > 1: continue
            if dr == 0 and abs(dc) == 1: # Same row
                neighbors[i].append(ni)
            elif abs(dr) == 1: # Adjacent row logic
                row_len = layout[r]
                next_len = layout[nr]
                if next_len > row_len:
                    if nc in [c, c + 1]: neighbors[i].append(ni)
                elif next_len < row_len:
                    if nc in [c, c - 1]: neighbors[i].append(ni)
                else: # Only in expansion center rows
                    offset = 1 if nr > r else -1
                    if nc in [c, c + offset]: neighbors[i].append(ni)
    return neighbors

def solve_resources(idx, board, res_pool, neighbors, config):
    """Phase 1: Place resources on the board."""
    if idx == len(board):
        return True

    # Get unique resources to try at this position to reduce search breadth
    unique_res = list(set(res_pool))
    random.shuffle(unique_res)

    # Desert Center Constraint Indices
    center_indices = [13, 16] if config['is_exp'] else [9]

    for res in unique_res:
        # Constraint: Desert Center
        if config['center_desert']:
            if (idx in center_indices and res != 'desert') or (idx not in center_indices and res == 'desert'):
                continue

        # Constraint: Same Resources Can't Touch
        if config['no_adj_res']:
            if any(board[n] and board[n]['resource'] == res for n in neighbors[idx]):
                continue

        # Place resource
        board[idx] = {'resource': res, 'number': None}
        res_pool.remove(res)
        
        if solve_resources(idx + 1, board, res_pool, neighbors, config):
            return True
            
        # Backtrack
        res_pool.append(res)
        board[idx] = None
        
    return False

def solve_numbers(idx, board, num_pool, neighbors, config):
    """Phase 2: Place numbers on the pre-generated resource layout."""
    if idx == len(board):
        return True

    # Skip deserts
    if board[idx]['resource'] == 'desert':
        return solve_numbers(idx + 1, board, num_pool, neighbors, config)

    unique_nums = list(set(num_pool))
    random.shuffle(unique_nums)

    for num in unique_nums:
        # Constraint: 6 & 8 Can't Touch
        if config['no_adj_red'] and num in [6, 8]:
            if any(board[n] and board[n].get('number') in [6, 8] for n in neighbors[idx]):
                continue
        
        # Constraint: Same Numbers Can't Touch
        if config['no_same_nums']:
            if any(board[n] and board[n].get('number') == num for n in neighbors[idx]):
                continue

        # Place number
        board[idx]['number'] = num
        num_pool.remove(num)
        
        if solve_numbers(idx + 1, board, num_pool, neighbors, config):
            return True
            
        # Backtrack
        num_pool.append(num)
        board[idx]['number'] = None
        
    return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate')
def generate():
    is_exp = request.args.get('expansion') == 'true'
    config = {
        'is_exp': is_exp,
        'no_adj_res': request.args.get('no_adj_res') == 'true',
        'no_adj_red': request.args.get('no_adj_red') == 'true',
        'no_same_nums': request.args.get('no_same_nums') == 'true',
        'center_desert': request.args.get('center_desert') == 'true'
    }
    
    layout = [3, 4, 5, 6, 5, 4, 3] if is_exp else [3, 4, 5, 4, 3]
    neighbors = get_neighbors_map(layout)
    
    # Try multiple shuffles in case a specific path is logically impossible
    for attempt in range(20):
        res_pool = EXP_RES[:] if is_exp else BASE_RES[:]
        num_pool = EXP_NUMS[:] if is_exp else BASE_NUMS[:]
        board = [None] * len(res_pool)

        if solve_resources(0, board, res_pool, neighbors, config):
            if solve_numbers(0, board, num_pool, neighbors, config):
                return jsonify(board)
                
    return jsonify({"error": "Failed to find a valid board. Try relaxing the rules."}), 400

if __name__ == '__main__':
    # Android specific setup
    if platform.system() == 'Android':
        from android.permissions import Permission, request_permissions
        request_permissions([Permission.INTERNET, Permission.WAKE_LOCK])
    
    # Run on local network for Android testing
    app.run(debug=False, port=8080, threaded=True)
