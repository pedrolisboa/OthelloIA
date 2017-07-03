class FirstMethodPlayer:
    def __init__(self, color):
        self.color = color
        self.counter = 0



    def evaluator(self, stateBoard):
        if self.color == stateBoard.WHITE:
            opponent = stateBoard.BLACK
        else:
            opponent = stateBoard.WHITE

        """if (stateBoard.valid_moves(self.color).__len__() <= 0):
            score = stateBoard.score()
            if (((score[0] > score[1]) and (self.color == stateBoard.WHITE)) or ((score[0] < score[1]) and (self.color == stateBoard.BLACK))):
                return float('inf')
            else:
                return float('-inf')"""

        weights = [10,801.724,382.026,78.922,74.396,10]
        if self.counter > 19:
            weights = [5000,801.724,382.026,78.922,74.396,10]

        from itertools import combinations, product
        directions = dict([(3, [(i, j) for i in [0, 1] for j in [0, 1] if i != 0 or j != 0]),
                           (10, [(i, j) for i in [0, -1] for j in [0, -1] if i != 0 or j != 0]),
                           (24, [(i, j) for i in [0, 1] for j in [0, -1] if i != 0 or j != 0]),
                           (17, [(i, j) for i in [0, -1] for j in [0, -1] if i != 0 or j != 0])])
        corners = [[1, 1], [1, 8], [8, 1], [8, 8]]

        # Piece Difference
        bp = 0
        wp = 0
        bc = 0
        wc = 0
        bf = 0
        wf = 0
        bl = 0
        wl = 0
        for i in range(1,9):
            for j in range(1,9):
                # Piece Difference
                if (stateBoard.get_square_color(i,j) == opponent):
                    wp += 1
                elif (stateBoard.get_square_color(i,j) == self.color):
                    bp += 1

                #Corner Occupancy
                if [i,j] in corners:
                    if (stateBoard.get_square_color(i, j) == opponent):
                        wc += 1
                    elif (stateBoard.get_square_color(i, j) == self.color):
                        bc += 1
                        # Corner Closeness
                        if i in [1,8] and j in [1,8]:
                            if (stateBoard.get_square_color(i, j) == '.'):
                                for (offsetX, offsetY) in directions[2 * i + j]:
                                    piece = stateBoard.get_square_color(i + offsetX, j + offsetY)
                                    if piece == self.color:
                                        bl += 1
                                    elif piece == opponent:
                                        wl += 1
                #Frontier Disks
                        if stateBoard.get_square_color(i+1, j) == '.' or \
                            stateBoard.get_square_color(i+1, j+1) == '.' or \
                            stateBoard.get_square_color(i, j+1) == '.' or \
                            stateBoard.get_square_color(i-1, j) == '.' or \
                            stateBoard.get_square_color(i-1, j-1) == '.' or \
                            stateBoard.get_square_color(i, j-1) == '.':
                            if (stateBoard.get_square_color(i, j) == opponent):
                                wf += 1
                            elif (stateBoard.get_square_color(i, j) == self.color):
                                bf += 1
        # Mobility
        bm=(stateBoard.valid_moves(self.color).__len__())
        wm = (stateBoard.valid_moves(opponent).__len__())
        if bp > wp:
            p = 100 * bp / (bp + wp)
        elif bp < wp:
            p = -100 * wp / (bp + wp)
        else:  # B==W
            p = 0
        # Mobility
        if bm > wm:
            m = 100 * bm / (bm + wm)
        elif bm < wm:
            m = -100 * wm / (bm + wm)
        else:  # B==W
            m = 0
        if (~bm | ~wm):
            m = 0
        # Frontier Discs
        if bf > wf:
            f = -100 * bf / (bf + wf)
        elif bf < wf:
            f = 100 * wf / (bf + wf)
        else:  # B==W
            f = 0
        # Corner Occupancy
        c = 25 * bc - 25 * wc
        # Corner Closeness
        l = -12.5 * bl + 12.5 * wl
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
        if (~len((copyState.valid_moves(self.color))) and search_counter)or (spentTime+time()-startTime>=(limitTime-TOL)):
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
        _, bestMove = self.fs_alphabeta(0,stateBoard,0,0.6, float('-inf'), float('inf'), 0, True)
        spent = (time() - start)
        print "TIME "
        print spent
        return bestMove
