import numpy as np
import matplotlib.pyplot as plt
from bresenham import bresenham
#%matplotlib inline
plt.rcParams['figure.figsize'] = 12, 12
def bres(p1, p2): 
    """
    Note this solution requires `x1` < `x2` and `y1` < `y2`.
    """
    x1, y1 = p1
    x2, y2 = p2
    cells = []
    m = (y2-y1)/(x2-x1)
    x = x1
    y = y1
    cells.append([x, y])
    while (x<x2)and (y<y2):
        #for y in range(y1,(y2+1))
        line = m*(x) + 0
        if line > (y+0.25):
            y += 1
        else:
            x += 1
        # if (y+m)>(y+0.5):
        #     x +=1
        #     y +=1
        # else:
        #     x +=1
        #     y =y
        cells.append([x, y])
    # TODO: Determine valid grid cells
        
    return np.array(cells)
if __name__ == "__main__":
    p1 = (0, 0)
    p2 = (7, 5)

    cells = bres(p1, p2)
    # print(cells)

    plt.plot([p1[0], p2[0]], [p1[1], p2[1]])


    for q in cells:
        plt.plot([q[0], q[0]+1], [q[1], q[1]], 'k')
        plt.plot([q[0], q[0]+1], [q[1]+1, q[1]+1], 'k')
        plt.plot([q[0], q[0]], [q[1],q[1]+1], 'k')
        plt.plot([q[0]+1, q[0]+1], [q[1], q[1]+1], 'k')

    plt.grid()
    plt.axis('equal')
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.title("Integer based Bresenham algorithm")
    plt.show()

    # using python library
    # Note: you can run this for any (x1, y1, x2, y2)
    line = (0, 0, 7, 5)

    cells = list(bresenham(line[0], line[1], line[2], line[3]))
    print(cells)

    plt.plot([line[0], line[2]], [line[1], line[3]])


    for q in cells:
        plt.plot([q[0], q[0]+1], [q[1], q[1]], 'k')
        plt.plot([q[0], q[0]+1], [q[1]+1, q[1]+1], 'k')
        plt.plot([q[0], q[0]], [q[1],q[1]+1], 'k')
        plt.plot([q[0]+1, q[0]+1], [q[1], q[1]+1], 'k')

    plt.grid()
    plt.axis('equal')
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.title("Python package Bresenham algorithm")
    plt.show()