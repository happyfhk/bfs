from collections import deque

dx=[-1,1,0,0]
dy=[0,0,-1,1]

n,m=map(int,input().split())

maze=[list(map(int,input().split())) for _ in range(n)]
visited=[[False]*m for _ in range(n)]
way=[[None]*m for _ in range(n)]
see=True # 원래는 False
dp=[[0]*m for _ in range(n)]

def bfs():
    global n,m
    q=deque()
    q.append((0,0))
    visited[0][0]=True

    while(q):
        y,x=q.popleft()

        if(y==n-1 and x==m-1):
            print(f"{dp[y][x]}만큼의 거리가 걸립니다")
            break

        for i in range(4):
            ny=y+dy[i]
            nx=x+dx[i]

            if(0<=ny<n and 0<=nx<m):
                if(maze[ny][nx]==0 and visited[ny][nx]==False):
                    visited[ny][nx]=True
                    dp[ny][nx]=dp[y][x]+1
                    way[ny][nx]=(y,x)
                    q.append((ny,nx))
    if(visited[n-1][m-1]==False):
        print("탈출할 수 없습니다")
        return
    else:
        path=[]
        x=m-1
        y=n=1
        path.append((y,x))

        while(not(x==0 and y==0)):
            path.append((y,x))
            y,x=way[y][x]
        
        path.append((0,0))
        path.reverse()

        if(see):
            for xy in path:
                print(f"({xy[1]},{xy[0]})")
    return

bfs()