def p(g):
    H=len(g); W=len(g[0])
    out=[[0]*W for _ in range(H)]
    r=0
    while r<H:
        if any(g[r]):
            R0=r
            while r<H and any(g[r]): r+=1
            R1=r-1
            cells=[(rr,c) for rr in range(R0,R1+1) for c in range(W) if g[rr][c]]
            C0=min(c for _,c in cells); C1=max(c for _,c in cells)
            color=g[cells[0][0]][cells[0][1]]
            row=R0; col=C0; tall=R1-R0+1; wide=C1-C0+1
            for k in range(wide-tall+2):
                out[row][col+k+1]=color
                out[row+tall-1][col+k+tall-2]=color
            for k in range(1,tall-1):
                out[row+k][col+k]=color
                out[row+k][min(col+k+wide-tall+2, col+wide-1)]=color
        else:
            r+=1
    return out
