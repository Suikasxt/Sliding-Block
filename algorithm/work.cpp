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
	//�����ͼ��Сn��m��
	scanf("%d%d", &n, &m);
	int* a = new int[n*m];
	
	//�����ʼ��ͼ
	for (int i = 0; i < n; i++)
	for (int j = 0; j < m; j++){
		scanf("%d", a+i*m+j);
	}
	
	//�������5���ƶ�
	for (int t = 0; t < 5; t++){
		int x, y;
		//�ҵ��ո�λ�ã���0��ʾ��
		for (int i = 0; i < n; i++)
		for (int j = 0; j < m; j++)
		if (a[i*m+j] == 0){
			x = i;
			y = j;
		}
		
		//��������ڵĸ��ӽ���
		for(;;){
			int k = rand()&3;
			int _x = x+f[k][0];
			int _y = y+f[k][1];
			if (min(_x, _y)>=0 && _x<n && _y<m){
				swap(a[_x*m+_y], a[x*m+y]);
				break;
			}
		}
		//���һ��n*m������ʹ�ÿո����
		printf("%d\n", a[x*m+y]);
		//ˢ�»�����
		fflush(stdout);
	}
	//Over��ʾ�������
	printf("Over\n"); 
	fflush(stdout);
	delete []a;
}

