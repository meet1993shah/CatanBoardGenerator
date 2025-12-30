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
                # Catan uses a specific stagger: 
                # In rows where length increases, neighbors are [c, c+1]
                # In rows where length decreases, neighbors are [c, c-1]
                # In rows where length is same, neighbors are [c, c +/- 1]
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

def solve_backtrack(idx, board, resources, numbers, neighbors, config):
    if idx == len(board):
        return True

    # Try every available resource for this tile
    available_res = sorted(list(set(resources)))
    random.shuffle(available_res)

    for res in available_res:
        # Check Desert Center Constraint
        if config['center_desert']:
            center_indices = [13, 16] if config['is_exp'] else [9]
            if (idx in center_indices and res != 'desert') or (idx not in center_indices and res == 'desert' and resources.count('desert') == (2 if config['is_exp'] and idx < 14 else 1)):
                continue

        # Check Resource Adjacency
        if config['no_adj_res']:
            if any(board[n] and board[n]['resource'] == res for n in neighbors[idx]):
                continue

        # If it's not desert, try a number
        if res != 'desert':
            available_nums = sorted(list(set(numbers)))
            random.shuffle(available_nums)
            for num in available_nums:
                # Check Number Adjacency
                if config['no_adj_red'] and num in [6, 8]:
                    if any(board[n] and board[n]['number'] in [6, 8] for n in neighbors[idx]):
                        continue
                if config['no_same_nums']:
                    if any(board[n] and board[n]['number'] == num for n in neighbors[idx]):
                        continue
                
                # Place and Recurse
                board[idx] = {'resource': res, 'number': num}
                resources.remove(res)
                numbers.remove(num)
                if solve_backtrack(idx + 1, board, resources, numbers, neighbors, config):
                    return True
                # Backtrack
                resources.append(res)
                numbers.append(num)
                board[idx] = None
        else:
            # Place Desert and Recurse
            board[idx] = {'resource': res, 'number': None}
            resources.remove(res)
            if solve_backtrack(idx + 1, board, resources, numbers, neighbors, config):
                return True
            resources.append(res)
            board[idx] = None

    return False

@app.route('/')
def index(): return render_template('index.html')

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
    resources = EXP_RES[:] if is_exp else BASE_RES[:]
    numbers = EXP_NUMS[:] if is_exp else BASE_NUMS[:]
    board = [None] * len(resources)

    if solve_backtrack(0, board, resources, numbers, neighbors, config):
        return jsonify(board)
    return jsonify({"error": "No valid board exists for these rules"}), 400

if __name__ == '__main__':
    # Android/Buildozer specific startup
    if platform.system() == 'Android':
        from android.permissions import Permission, request_permissions
        # INTERNET is the primary requirement; WAKE_LOCK prevents sleep during video
        request_permissions([Permission.INTERNET, Permission.WAKE_LOCK])
    
    # 0.0.0.0 allows access from other devices on the same network
    # threaded=True is required to handle background HLS.js segment requests
    app.run(debug=False, port=8080, threaded=True)
