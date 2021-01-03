import numpy as np
counter = 0
for n in [[3, 3], [4, 5], [8, 10]]:
    for j in range(10):
        f = open('%02d.in'%counter, 'w')
        f.write('%d %d\n'%(n[0], n[1]))
        l = np.arange(n[0]*n[1])
        np.random.shuffle(l)
        for i in l:
            f.write('%d '%(i))
        f.close()
        counter+=1
