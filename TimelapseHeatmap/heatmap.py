import matplotlib.pyplot as plt
from PIL import Image
from sklearn.datasets._samples_generator import make_blobs
import seaborn as sns


def create_clusters(centers,n_samples,deviations):
    X,truth = make_blobs(n_samples=n_samples, centers=centers,cluster_std=deviations,random_state=42)

    dx = []   # x axis points
    dy = []     # y axis points
    for coords in X:
      dx.append(coords[0])
      dy.append(coords[1])
    
    
    
    ### 
    ### WHEN TIME COMES WHERE IT'S NEEDED TO LIMIT THE CLUSTERS WITHIN A CERTAIN
    ### ROOM, JUST SIMPLY ITERATE THROUGH DX AND DY ARRAY, AND REMOVE THE POINTS
    ### WICH ARE OUTISDE THE ROOM
    ###
    return dx,dy


centers = [(300,650), 
    (250,500), 
    (400,380),
    (300,300),
    (470,290),
    (550,150)]   # AP's coordinates

n_samples = [3,6,20,10,4,3]  # number of people conected per API, sorted according to centers

deviations = [3*2,6*2,20*2,10*2,4*2,3*2] # deviation of the clusters, the more people are connected to a certain AP, bigger the deviation.


dx,dy = create_clusters(centers,n_samples,deviations) # create clusters


plt.scatter(dx, dy)
plt.title(f"Example of a mixture of {len(centers)} distributions")
plt.xlabel("x")
plt.ylabel("y")


Image1 = Image.open("input/piso1.png")
width, height = Image1.size
plt.imshow(Image1, interpolation=None) # I would add interpolation='none'
sns.kdeplot(x=dx,y=dy,shade=True,thresh=0.05,alpha=0.5,cmap="magma",levels=5,clip=((0,height)),bw_adjust=0.8)
plt.savefig('output/piso1.png',bbox_inches='tight')
plt.show()
