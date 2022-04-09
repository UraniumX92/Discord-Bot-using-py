import numpy as np
import random

def findl(listx,value):
    ind = -1
    for i,item in enumerate(listx):
        if item == value:
            ind = i
            break
    return ind

def onestepaway(arr3x3:"np.ndarray",value):
    """
    when given player value is 1 step away from winning the game, this function returns the (x,y) index where the last mark should be placed to win.
    if game is not 1 step away from winning then this function returns `None`
    """
    # Making a copy so that the original array shouldn't get changed if there's any change.
    arr2d = arr3x3.copy()

    # Case 1,2,3: Rows
    for i in range(3):
        if (arr2d[i, 0] == 0 and arr2d[i, 1] == value and arr2d[i, 2] == value):
            return i, 0
        if (arr2d[i, 0] == value and arr2d[i, 1] == 0 and arr2d[i, 2] == value):
            return i, 1
        if (arr2d[i, 0] == value and arr2d[i, 1] == value and arr2d[i, 2] == 0):
            return i, 2

    # Case 4,5,6: Columns
    # Transposing the matrix to interchange rows with columns
    arr2d = np.stack(arr2d,axis=1)
    for j in range(3):
        if (arr2d[j, 0] == 0 and arr2d[j, 1] == value and arr2d[j, 2] == value):
            return 0, j
        if (arr2d[j, 0] == value and arr2d[j, 1] == 0 and arr2d[j, 2] == value):
            return 1, j
        if (arr2d[j, 0] == value and arr2d[j, 1] == value and arr2d[j, 2] == 0):
            return 2, j
    # Transposing the transposed matrix to get the original matrix
    arr2d = np.stack(arr2d,axis=1)

    # Case 7: backslash diagonal '\'
    diaglist = []
    for i in range(3):
        for j in range(3):
            if i==j:
                if arr2d[i,j] == value or arr2d[i,j]==0:
                    diaglist.append(arr2d[i,j]==value)

    if len(diaglist) == 3:
        num = findl(diaglist,False)
        if num>=0:
            diaglist.pop(num)
            if False in diaglist:
                pass
            else:
                return num,num

    # Case 8: slash diagonal '/'
    # Interchanging row 0 and row 2 to get slash like diagonal
    temp = arr2d[0].copy()
    arr2d[0] = arr2d[2].copy()
    arr2d[2] = temp.copy()

    diaglist = []
    for i in range(3):
        for j in range(3):
            if i == j:
                if arr2d[i, j] == value or arr2d[i, j] == 0:
                    diaglist.append(arr2d[i, j] == value)

    if len(diaglist) == 3:
        num = findl(diaglist, False)
        if num>=0:
            diaglist.pop(num)
            if False in diaglist:
                return None
            if num == 0:
                return 2,num
            if num == 1:
                return num,num
            if num == 2:
                return 0,num

    # Case 9: Not nearing the win
    return None


def winner(arr3x3:"np.ndarray",value):
    # Making a copy so that the original array shouldn't get changed if there's any change.
    arr2d = arr3x3.copy()

    # Case 1,2,3: Rows
    for i in range(3):
        count = 0
        for j in range(3):
            if arr2d[i,j] == value:
                count += 1
        if count==3:
            return True

    # Case 4,5,6: Columns
    # Transposing the matrix to interchange rows with columns
    arr2d = np.stack(arr2d, axis=1)
    for i in range(3):
        count = 0
        for j in range(3):
            if arr2d[i, j] == value:
                count += 1
        if count == 3:
            return True
    # Transposing the transposed matrix to get the original matrix
    arr2d = np.stack(arr2d, axis=1)

    # Case 7: backslash diagonal '\'
    diagcount = 0
    for i in range(3):
        for j in range(3):
            if i == j:
                if arr2d[i, j] == value:
                    diagcount += 1

    if diagcount == 3:
        return True

    # Case 8: slash diagonal '/'
    # Interchanging row 0 and row 2 to get slash like diagonal
    temp = arr2d[0].copy()
    arr2d[0] = arr2d[2].copy()
    arr2d[2] = temp.copy()

    diagcount = 0
    for i in range(3):
        for j in range(3):
            if i == j:
                if arr2d[i, j] == value:
                    diagcount += 1

    if diagcount == 3:
        return True

    # Case 9: Not winning
    return False

def tictactoe():
    plays = 0
    matrix = np.array([[0]*3 for _i in range(3)])
    sides = [(0,1),(1,2),(2,1),(1,0)]
    corners = [(0,0),(0,2),(2,2),(2,0)]
    middle = (1,1)
    user = 2
    comp = 1
    won = False
    draw = False
    available_slots = []
    # Opposite corners for given side
    opp_corners = {
        sides[0] : ((2,0),(2,2)),
        sides[1] : ((0,0),(2,0)),
        sides[2] : ((0,0),(0,2)),
        sides[3] : ((0,2),(2,2))
    }

    # Opposite corner for given corner
    c2c_opp = {
        corners[0] : corners[2],
        corners[2] : corners[0],
        corners[1] : corners[3],
        corners[3] : corners[1]
    }

    for i in range(3):
        for j in range(3):
            available_slots.append(tuple((i,j)))

    turn = 0
    ht = ['h','t']
    res = random.choice(ht)
    if res == 'h':
        turn = 1
    else:
        pass

    while (not won) and (not draw):
        print(matrix)
        userind = None
        if turn%2==1:
            print("Your turn")
            while userind not in available_slots:
                userind = input("Enter x,y: ").split(',')
                userind = tuple((int(userind[0]),int(userind[1])))

            matrix[userind] = user
            plays += 1
            available_slots.remove(userind)
            won = winner(matrix, user)
            if won:
                print(matrix)
                print("You won")
                continue
            if len(available_slots) == 0:
                print(matrix)
                print("It's a draw game")
                draw = True
                continue
        else:
            print("computer's turn")
            if plays == 0:
                compind = random.choice(corners)
            else:
                # Check if bot has any chance to win the game
                compind = onestepaway(matrix,comp)
                if not compind:
                    # Check if the user is about to win, if True, then try to block user from winning
                    compind = onestepaway(matrix,user)
                if not compind:
                    # play on middle when more than 3 plays are done and middle is still empty
                    if middle in available_slots or plays == 0:
                        compind = middle
                    else:
                        """
                        X _ _
                        _ O _   Here: X is user, O is bot
                        _ _ X
                        
                        if this is the situation then place at any of 4 sides
                        """
                        two_corners = None
                        for corner in corners:
                            if matrix[c2c_opp[corner]] == user and matrix[corner] == user and matrix[middle] == comp:
                                two_corners = (corner,c2c_opp[corner])
                        if two_corners:
                            filtered_sides = list(filter(lambda x:x in available_slots,sides))
                            compind = random.choice(filtered_sides)
                        else:
                            # If user placed on corners and opposite corner is empty, then place on opposite corner
                            if userind in corners:
                                if c2c_opp[userind] in available_slots:
                                    compind = c2c_opp[userind]
                                else:
                                    if middle in available_slots:
                                        compind = middle
                                    else:
                                        compind = random.choice(available_slots)
                            else:
                                # If user placed on sides and any of the opposite corners of that side are empty, then place on any one of the opposite corners
                                if userind in sides:
                                    compind = random.choice(opp_corners[userind])
                                    if compind not in available_slots:
                                        if middle in available_slots:
                                            compind = middle
                                        else:
                                            compind = random.choice(available_slots)
                                else:
                                    # If Corners are available, then place on corner
                                    filetered_corners = list(filter(lambda x:x in available_slots,corners))
                                    compind = random.choice(filetered_corners) if len(filetered_corners) > 0 else None
                                    if compind not in available_slots or not compind:
                                        if middle in available_slots:
                                            compind = middle
                                        # If any of the above conditions are not met, simply choose any random slot and place there
                                        else:
                                            compind = random.choice(available_slots)

            matrix[compind] = comp
            plays += 1
            available_slots.remove(compind)
            won = winner(matrix,comp)
            if won:
                print(matrix)
                print("Computer won")
                continue
            if len(available_slots) == 0:
                print(matrix)
                print("It's a draw game")
                draw = True
                continue
        turn += 1

if __name__ == '__main__':
    repeat = 'y'
    while repeat=='y':
        tictactoe()
        repeat = input("do you want to play again? y/n : ").lower()