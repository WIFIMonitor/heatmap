from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import multivariate_normal


def points_to_gaussian_heatmap(centers, height, width, scale):
    gaussians = []
    for y,x in centers:
        s = np.eye(2)*scale
        g = multivariate_normal(mean=(x,y), cov=s)
        gaussians.append(g)

    # create a grid of (x,y) coordinates at which to evaluate the kernels
    x = np.arange(0, width)
    y = np.arange(0, height)
    xx, yy = np.meshgrid(x,y)
    xxyy = np.stack([xx.ravel(), yy.ravel()]).T
    
    # evaluate kernels at grid points
    zz = sum(g.pdf(xxyy) for g in gaussians)

    img = zz.reshape((height,width))
    return img

SCALE = 2000  # increase scale to make larger gaussians
CENTERS = [(650,300), 
           (500,250), 
           (380,400),
           (300,300),
           (290,470),
           (150,550)] # center points of the gaussians (y,x)


Image1 = Image.open("input/piso1.png")
width, height = Image1.size
print(width)
print(height)
plt.imshow(Image1) # I would add interpolation='none'
img = points_to_gaussian_heatmap(CENTERS, height, width, SCALE)
plt.imshow(img,alpha=0.7,cmap="magma")
plt.savefig('output/piso1.png')
plt.show()

### HEIGHT AND WIDTH VALUES ARE SWITCHED, LATER WILL CHANGE THEM
