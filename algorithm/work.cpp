#include<ctime>
#include<cstdio>
#include<cstring>
#include<algorithm>
using namespace std;

const int f[4][2] = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
int numberCount = 0;
int n, m;
int main(){
	srand(time(0));
	//读入地图大小n行m列
	scanf("%d%d", &n, &m);
	int* a = new int[n*m];
	
	//读入初始地图
	for (int i = 0; i < n; i++)
	for (int j = 0; j < m; j++){
		scanf("%d", a+i*m+j);
	}
	
	//随机进行5次移动
	for (int t = 0; t < 5; t++){
		int x, y;
		//找到空格位置（用0表示）
		for (int i = 0; i < n; i++)
		for (int j = 0; j < m; j++)
		if (a[i*m+j] == 0){
			x = i;
			y = j;
		}
		
		//随机跟相邻的格子交换
		for(;;){
			int k = rand()&3;
			int _x = x+f[k][0];
			int _y = y+f[k][1];
			if (min(_x, _y)>=0 && _x<n && _y<m){
				swap(a[_x*m+_y], a[x*m+y]);
				break;
			}
		}
		//输出一行n*m个数，使用空格隔开
		printf("%d\n", a[x*m+y]);
		//刷新缓冲区
		fflush(stdout);
	}
	//Over提示输出结束
	printf("Over\n"); 
	fflush(stdout);
	delete []a;
}

