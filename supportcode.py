import os
from skimage import measure
#from skimage.measure import structural_similarity as ssim #old
import matplotlib.pyplot as plt
import numpy as np
import cv2
import glob

#from skimage.metrics import structural_similarity



def mse(imageA, imageB):
	# the 'Mean Squared Error' between the two images is the
	# sum of the squared difference between the two images;
	# NOTE: the two images must have the same dimension
	err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
	err /= float(imageA.shape[0] * imageA.shape[1])
	
	# return the MSE, the lower the error, the more "similar"
	# the two images are
	return err

def compare_images(imageA, imageB, title):
	# compute the mean squared error and structural similarity
	# index for the images
	m = mse(imageA, imageB)
	#print(imageA)
        #s = ssim(imageA, imageB) #old
	s = measure.compare_ssim(imageA, imageB, multichannel=True)
	print(s)
        # setup the figure
	fig = plt.figure(title)
	plt.suptitle("MSE: %.2f, SSIM: %.2f" % (m, s))
	

	# show first image
	ax = fig.add_subplot(1, 2, 1)
	plt.imshow(imageA, cmap = plt.cm.gray)
	plt.axis("off")

	# show the second image
	ax = fig.add_subplot(1, 2, 2)
	plt.imshow(imageB, cmap = plt.cm.gray)
	plt.axis("off")

	# show the images
	#plt.show()
	return s




diseaselist=os.listdir('static/Dataset')
print(diseaselist)
filename='c.jpeg'
ci=cv2.imread(filename)
gray = cv2.cvtColor(ci, cv2.COLOR_BGR2GRAY)
cv2.imwrite("static/Grayscale/"+filename,gray)
cv2.imshow("org",gray)
cv2.waitKey()

thresh = cv2.cvtColor(ci, cv2.COLOR_BGR2HSV)
cv2.imwrite("static/Threhold/"+filename,thresh)
cv2.imshow("org",thresh)
cv2.waitKey()

lower_green = np.array([34, 177, 76])
upper_green = np.array([255, 255, 255])
hsv_img = cv2.cvtColor(ci, cv2.COLOR_BGR2HSV)
binary = cv2.inRange(hsv_img, lower_green, upper_green)
cv2.imwrite("static/Binary/"+filename,gray)
cv2.imshow("org",binary)
cv2.waitKey()


'''       
width = 400
height = 400
dim = (width, height)
oresized = cv2.resize(ci, dim, interpolation = cv2.INTER_AREA)
flagger=1
for i in range(len(diseaselist)):
    if flagger==1:
        files = glob.glob('static/Dataset/'+diseaselist[i]+'/*')
        #print(len(files))
        for file in files:
            # resize image
            print(file)
            oi=cv2.imread(file)
            resized = cv2.resize(oi, dim, interpolation = cv2.INTER_AREA)
            #original = cv2.cvtColor(file, cv2.COLOR_BGR2GRAY)
            #cv2.imshow("comp",oresized)
            #cv2.waitKey()
            #cv2.imshow("org",resized)
            #cv2.waitKey()
            #ssim_score = structural_similarity(oresized, resized, multichannel=True)
            #print(ssim_score)
            ssimscore=compare_images(oresized, resized, "Comparison")
            if ssimscore>0.3:
                print(diseaselist[i])
                flagger=0
                break

'''






