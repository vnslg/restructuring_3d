import numpy as np
import cv2 as cv
import glob

criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
objp = np.zeros((6*7, 3), np.float32)
objp[:, :2] = np.mgrid[0:7, 0:6].T.reshape(-1, 2)

objpoints = []
imgpoints = []
images = glob.glob('*.jpg')

for fname in images:
    img = cv.imread(fname)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    # Localiza as bordas do tabuleiro
    ret, corners = cv.findChessboardCorners(gray, (7, 6), None)
    if ret is True:
        objpoints.append(objp)
        corners2 = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        imgpoints.append(corners)
        # Draw and display the corners
        cv.drawChessboardCorners(img, (7, 6), corners2, ret)
        cv.imshow('img', img)
        cv.waitKey(500)

ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

np.savez('B.npz', mtx=mtx, dist=dist, rvecs=rvecs, tvecs=tvecs)
input("Clique ENTER para continuar")

cv.destroyAllWindows()

# Localiza a imagem que será identificada e desenhada sobre
img = cv.imread('img_tabuleiro.jpg')
h,  w = img.shape[:2]
newcameramtx, roi = cv.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))

# Calibração de Camera
dst = cv.undistort(img, mtx, dist, None, newcameramtx)

# Corta a imagem
x, y, w, h = roi
dst = dst[y:y+h, x:x+w]
cv.imwrite('calib_camera.png', dst)


# Carrega o arquivo com os pontos identificados
with np.load('B.npz') as X:
    mtx, dist, _, _ = [X[i] for i in ('mtx', 'dist', 'rvecs', 'tvecs')]


criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
objp = np.zeros((6*7, 3), np.float32)
objp[:, :2] = np.mgrid[0:7, 0:6].T.reshape(-1, 2)


# O código abaixo permite o desenho das bordas do cubo, apenas
def draw_corners(img, corners, imgpts):
    corner = tuple(corners[0].ravel())

    corner_a = int(corner[0])
    corner_b = int(corner[1])

    pontos_imagem_1 = tuple(imgpts[0].ravel())
    pontos_imagem_2 = tuple(imgpts[1].ravel())
    pontos_imagem_3 = tuple(imgpts[2].ravel())

    img_pt1_a = int(pontos_imagem_1[0])
    img_pt1_b = int(pontos_imagem_1[1])

    img_pt2_a = int(pontos_imagem_2[0])
    img_pt2_b = int(pontos_imagem_2[1])

    img_pt3_a = int(pontos_imagem_3[0])
    img_pt3_b = int(pontos_imagem_3[1])

    img = cv.line(img, (corner_a, corner_b), (img_pt1_a, img_pt1_b), (255, 0, 0), 5)
    img = cv.line(img, (corner_a, corner_b), (img_pt2_a, img_pt2_b), (0, 255, 0), 5)
    img = cv.line(img, (corner_a, corner_b), (img_pt3_a, img_pt3_b), (0, 0, 255), 5)

    return img


axis = np.float32([[3, 0, 0], [0, 3, 0], [0, 0, -3]]).reshape(-1, 3)

for fname in glob.glob('img_tabuleiro.jpg'):
    img = cv.imread(fname)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    ret, corners = cv.findChessboardCorners(gray, (7, 6), None)

    if ret is True:
        corners2 = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)

        # Find the rotation and translation vectors.
        ret, rvecs, tvecs = cv.solvePnP(objp, corners2, mtx, dist)

        # project 3D points to image plane
        imgpts, jac = cv.projectPoints(axis, rvecs, tvecs, mtx, dist)
        img = draw_corners(img, corners2, imgpts)

        cv.imshow('img', img)
        k = cv.waitKey(0) & 0xFF
        if k == ord('s'):
            cv.imwrite(fname[:6]+'.png', img)

cv.destroyAllWindows()


axis = np.float32([[0, 0, 0], [0, 3, 0], [3, 3, 0], [3, 0, 0],
                   [0, 0, -3], [0, 3, -3], [3, 3, -3], [3, 0, -3]])


def draw_cubo(img, corners, imgpts):
    imgpts = np.int32(imgpts).reshape(-1, 2)

    # draw ground floor in green
    img = cv.drawContours(img, [imgpts[:4]], -1, (0, 255, 0), -3)

    # draw pillars in blue color
    for i, j in zip(range(4), range(4, 8)):
        img = cv.line(img, tuple(imgpts[i]), tuple(imgpts[j]), 255, 3)

    # draw top layer in red color
    img = cv.drawContours(img, [imgpts[4:]], -1, (0, 0, 255), 3)

    return img


for fname in glob.glob('img_tabuleiro.jpg'):
    img = cv.imread(fname)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    ret, corners = cv.findChessboardCorners(gray, (7, 6), None)

    if ret is True:
        corners2 = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)

        # Find the rotation and translation vectors.
        ret, rvecs, tvecs = cv.solvePnP(objp, corners2, mtx, dist)

        # project 3D points to image plane
        imgpts, jac = cv.projectPoints(axis, rvecs, tvecs, mtx, dist)
        img = draw_cubo(img, corners2, imgpts)

        # cv.imwrite('resultado.png', img)
        cv.imshow('img', img)
        k = cv.waitKey(0) & 0xFF
        if k == ord('s'):
            cv.imwrite(fname[:6]+'.png', img)

cv.destroyAllWindows()
