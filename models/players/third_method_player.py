class ThirdMethodPlayer:
    def __init__(self, color):
        self.color = color
        self.corner_weights = [50, 30, 40, 15]
        self.mob_weights = [50, 50]
        self.counter = 0

    def evaluator(self, stateBoard):
        from itertools import combinations, product

        if self.counter < 5:
        #    weights = [400, 6100000.372176, 3000,7800.922, 7400000.396, 400000]
            weights = [0, 6100000.372176, 3000, 7800000.922, 0.396, 40]
        elif self.counter < 20:
        #    weights = [10,642761.372176,382000.026,145943.864676,553.764816,10]
            weights = [0, 642761.372176, 382000.026, 145943.864676, 553.764816, 300000]
        else:
            weights = [1000, 2, 100,2, 2, 2]
        if self.counter > 30:
            weights = [10000, 2, 5000, 2, 2000, 2]
        print(self.counter)
        b = 0
        w = 0
        value = 0

        if self.color == stateBoard.WHITE:
            opponent = stateBoard.BLACK
        else:
            opponent = stateBoard.WHITE

        fb, fw = 0, 0
        for i in range(1, 9):
            for j in range(1, 9):
                if (stateBoard.get_square_color(i, j) == opponent):
                    w += 1
                    for (adjacentX, adjacentY) in product((1, -1), repeat=2):
                        if stateBoard.get_square_color(i + adjacentX, j + adjacentY) == '.':
                            fb += 1
                elif (stateBoard.get_square_color(i, j) == self.color):
                    b += 1
                    for (adjacentX, adjacentY) in product((1, -1), repeat=2):
                        if stateBoard.get_square_color(i + adjacentX, j + adjacentY) == '.':
                            fw += 1
        # Piece Difference
        if b > w:
            p = 100 * b / (b + w)
        elif b < w:
            p = -100 * b / (b + w)
        else:  # B==W
            p = 0
        # Mobility
        m = p
        if (~b | ~w):
            m = 0
        # Frontier Discs
        if fb > fw:
            f = - 100 * fb / (fb + fw)
        elif fb < fw:
            f =   100 * fb / (fb + fw)
        else:
            f = 0
        # Corner Occupancy
        b, w = 0, 0
        for i in [1,8]:
            for j in [1,8]:
                corner = stateBoard.get_square_color(i, j)
                if corner == self.color:
                    b += 1
                elif corner == opponent:
                    w += 1
        c = 25 * b - 25 * w
        # Corner Closeness
        b, w = 0, 0
        directions = dict([(3, [(i, j) for i in [0, 1] for j in [0, 1] if i != 0 or j != 0]),
                           (10, [(i, j) for i in [0, -1] for j in [0, -1] if i != 0 or j != 0]),
                           (24, [(i, j) for i in [0, 1] for j in [0, -1] if i != 0 or j != 0]),
                           (17, [(i, j) for i in [0, -1] for j in [0, -1] if i != 0 or j != 0])])
        for i in [1, 8]:
            for j in [1, 8]:
                if stateBoard.get_square_color(i, j) == '.':
                    for (offsetX, offsetY) in directions[2 * i + j]:
                        piece = stateBoard.get_square_color(i + offsetX, j + offsetY)
                        print(offsetX, offsetY)
                        if piece == self.color:
                            b += 1
                        elif piece == opponent:
                            w += 1
        l = -12.5 * b + 12.5 * w
        # Disc squares
        V = [[20, -3, 11, 8],[-3, -7, -4, 1],[11, -4, 2, 2],[8, 1 , 2, -3]]
        d=0
        for line in range(1,9):
            for col in range(1,9):
                i=line-1
                j=col-1
                sigma=0
                if line>4:
                    i=-line+8
                if col>4:
                    j=-col+8
                if stateBoard.get_square_color(line,col) == opponent:
                    sigma = -1
                elif stateBoard.get_square_color(line,col) == self.color:
                    sigma = 1
                d+=sigma*V[i][j]

        max_player = self.color
        if self.color == stateBoard.WHITE:
            min_player = stateBoard.BLACK
        else:
            min_player = stateBoard.WHITE

        c = self.mobility(stateBoard, max_player, min_player, self.mob_weights)
        m = self.corner_mobility(stateBoard, max_player, min_player, self.corner_weights)

        ck = [p, c, l, m, f, d]
        value = 0
        for n in range(len(ck)):
            value+=ck[n]*weights[n]
        return value

    def shallowSearch(self,stateBoard):

        copyState = stateBoard.get_clone()
        valuesequence = []
        movesequence = []
        for move in stateBoard.valid_moves(self.color):
            copyState = copyState.get_clone()
            copyState.play(move, self.color)
            movevalue = 0
            movevalue = max(movevalue, self.evaluator(copyState))

            for child_move in copyState.valid_moves(self.color):
                child_copyState = copyState.get_clone()
                child_copyState.play(child_move, self.color)
                movevalue = max(movevalue, self.evaluator(child_copyState))
                """for grandson_move in child_copyState.valid_moves(self.color):
                    grandson_copyState = child_copyState.get_clone()
                    grandson_copyState.play(grandson_move, self.color)
                    movevalue = max(movevalue, self.evaluator(grandson_copyState))"""

            i=0
            for value in valuesequence:
                if movevalue>value:
                    movesequence.insert(i,move)
                    valuesequence.insert(i,movevalue)
                    break
                i+=1
            if i==len(valuesequence):
                movesequence.append(move)
                valuesequence.append(movevalue)

        #print valuesequence
        #print [(move.x,move.y) for move in movesequence]
        return movesequence



    def fs_alphabeta(self,move,stateBoard, spentTime,limitTime, alpha, beta, search_counter,player_max):
        #from copy import copy
        TOL = 0.1*limitTime
        from time import time
        startTime = time()
        copyState = stateBoard.get_clone()
        if search_counter:
            copyState.play(move, self.color)

        def debug_print():
            if ~(len(copyState.valid_moves(self.color))) or (spentTime+time()-startTime>=(limitTime-TOL)):
                return
            return

        movesequence = []
        if ~len((copyState.valid_moves(self.color))) and search_counter:
            movesequence += [move]
            return self.evaluator(copyState), movesequence

        debug_print()
        movesequence = []

        child_movesequence = []
        shallowSerachSequence = self.shallowSearch(stateBoard)
        if player_max: # MAX
            value = float('-inf')
            for move in shallowSerachSequence:
                child_value, child_movesequence = self.fs_alphabeta(move,copyState, spentTime+time()-startTime,limitTime, alpha, beta,search_counter + 1,False)
                value = max(value, child_value)

                if child_value >= alpha:
                    alpha = child_value
                    movesequence = [move]
                if (spentTime + time() - startTime >= (limitTime - TOL)):
                        return value, movesequence[0]
                if beta <= alpha:
                    break

        else:  # player_min
            value = float('inf')
            for move in shallowSerachSequence[::-1]:
                child_value, child_movesequence = self.fs_alphabeta(move,copyState, spentTime+time()-startTime,limitTime, alpha, beta, search_counter + 1, True)
                value = min(value, child_value)

                if child_value <= beta:
                    beta = child_value
                    movesequence = [move]
                if (spentTime + time() - startTime >= (limitTime - TOL)):
                    return value, movesequence[0]

                if beta <= alpha:
                    break

        debug_print()

        return value, movesequence[0]


    def play(self, board):
        return self.chooseNextMove(board)

    def chooseNextMove(self, stateBoard):
        from time import time
        self.counter += 1
        corners = [[1, 1], [1, 8], [8, 1], [8, 8]]
        for move in stateBoard.valid_moves(self.color):
            if [move.x,move.y] in corners:
                print "CORNER"
                return move
        start = time()
        _, bestMove = self.fs_alphabeta(0,stateBoard,0,0.5, float('-inf'), float('inf'), 0, True)
        spent = (time() - start)
        print "TIME "
        print spent
        return bestMove


    ########################################################
    # MISCELLANEOUS
    ########################################################
    def eval_heuristic(self,eval_max, eval_min):
        if eval_max + eval_min != 0:
            return 100 * (eval_max - eval_min) / \
                    (eval_max + eval_min)
        return 0

    def check_neighbourhood(self,board, player, (x,y)):
        friend_count, null_count, enemy_count = 0,0,0
        for i in [-1,1]:
            for j in [-1,1]:
                if x+i > 9 or y + j > 9 or x+i < 1 or y+j < 1:
                    square = board.get_square_color(x + i, y + j)
                    if square == player:
                        friend_count += 1
                    elif square == '.':
                        null_count += 1
                    else:
                        enemy_count +=1
        return friend_count,null_count,enemy_count

    #######################################################
    #FUNCOES DA HEURISTICA
    #######################################################

    def mobility(self,board, max_player, min_player,weights):
        max_player_actual_mob = len(board.valid_moves(max_player))
        min_player_actual_mob = len(board.valid_moves(min_player))

        actual_mobility = self.eval_heuristic(max_player_actual_mob, min_player_actual_mob)

        max_player_potential = 0
        min_player_potential = 0
        for i in range(1,9):
            for j in range(1,9):
                if board.get_square_color(i,j) == max_player:
                    player, null_squares, opponent = self.check_neighbourhood(board,max_player,(i,j))
                elif board.get_square_color(i,j) == min_player:
                    opponent, null_squares, player = self.check_neighbourhood(board, min_player, (i, j))
                else:
                    continue
                max_player_potential += opponent
                min_player_potential += player + null_squares

        potential_mobility = self.eval_heuristic(max_player_potential,min_player_potential)

        W_ACTUAL, W_POTENTIAL = 0,1
        return (weights[W_ACTUAL]*actual_mobility +  weights[W_POTENTIAL]*potential_mobility)/(weights[W_ACTUAL] +
                                                                                           weights[W_POTENTIAL])


    def corner_mobility(self,board, max_player, min_player, weights):
        # Calculate corner values for each player
        max_player_actual_corners = self.get_player_corner_pieces(board, max_player)
        min_player_actual_corners = self.get_player_corner_pieces(board, min_player)

        potential_corners, unlikely_corners, irreversible_corners = \
            self.get_potential_and_unlikely_corners(board,max_player,min_player)

        # Calculate heuristic blocks
        heuristic_actual_corners = self.eval_heuristic(max_player_actual_corners,
                                                  min_player_actual_corners)
        heuristic_potential_corners = self.eval_heuristic(potential_corners[max_player],
                                                     unlikely_corners[max_player])
        heuristic_unlikely_corners = self.eval_heuristic(potential_corners[max_player],
                                                     unlikely_corners[max_player])
        heuristic_irreversible_corners = self.eval_heuristic(irreversible_corners[max_player],
                                                        irreversible_corners[max_player])

        W_ACTUAL, W_POTENTIAL, W_UNLIKELY, W_IRREVERSIBLE = 0, 1, 2, 3
        return (weights[W_ACTUAL] * heuristic_actual_corners +
                weights[W_POTENTIAL] * heuristic_potential_corners +
                weights[W_UNLIKELY] * heuristic_unlikely_corners +
                weights[W_IRREVERSIBLE] * heuristic_irreversible_corners)/ (
                weights[W_ACTUAL] + weights[W_POTENTIAL] + weights[W_UNLIKELY] + weights[W_IRREVERSIBLE])

###############################################################
# FUNCOES DE SUPORTE PARA AS HEURISTICAS
###############################################################

    def get_player_corner_pieces(self, board, player_piece):
        return sum([1 if (board.get_square_color(i, j) == player_piece)
                    else 0 for i in [1, 8] for j in [1, 8]])

    def get_potential_and_unlikely_corners(self,board,max_player,min_player):
        offsets = dict([(1, [1, 2, 3, 4, 5, 6, 7]), (8, [-1, -2, -3, -4, -5, -6, -7])])
        potential_corners = {max_player:0,min_player:0}
        unlikely_corners =  {max_player:0,min_player:0}
        irreversible_corners = {max_player: 0, min_player: 0}

        for i in [1, 8]:
            for j in [1, 8]:
                corner_player = board.get_square_color(i,j)
                if corner_player == '.':
                    continue
                elif corner_player == max_player:
                    opponent = min_player
                else:
                    opponent = max_player
                for offsetX,offsetY in zip(offsets[i],offsets[j]): # row
                    NotAllyRow, NotAllyCol, NotAllyDiag = False,False,False
                    rowScan = board.get_square_color(i+offsetY, j)
                    if rowScan != max_player:
                        NotAllyRow = True
                        break
                for _ in range(1,7): # col
                    colScan = board.get_square_color(i,j+offsetX)
                    if colScan != max_player:
                        NotAllyCol = True
                        break
                for _ in range(1,7): # diagonal
                    diagScan = board.get_square_color(i+offsetX, j+offsetY)
                    if diagScan != max_player:
                        NotAllyDiag = True
                        break
                if NotAllyRow:
                    if rowScan == '.':
                        unlikely_corners[opponent] += 1
                    else:
                        potential_corners[opponent] += 1
                else:
                    irreversible_corners[corner_player] += 1
                if NotAllyCol:
                    if rowScan == '.':
                        unlikely_corners[opponent] += 1
                    else:
                        potential_corners[opponent] += 1
                else:
                    irreversible_corners[corner_player] += 1
                if NotAllyDiag:
                    if rowScan == '.':
                        unlikely_corners[opponent] += 1
                    else:
                        potential_corners[opponent] += 1
                else:
                    irreversible_corners[corner_player] += 1
        return potential_corners,unlikely_corners,irreversible_corners
