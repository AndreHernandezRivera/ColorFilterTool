import cv2
import glob
import numpy as np
from functools import partial
import sys
import os


class ColorFilter:
    VALID_TYPES = ['hmin', 'hmax', 'smin', 'smin', 'vmin', 'vmin']

    def __init__(self, name):
        self.name = name
        self.hmin, self.hmax = 0, 180
        self.smin, self.smax = 0, 255
        self.vmin, self.vmax = 0, 255
        self.img, self.img_hsv, self.mask = None, None, None
        self.CHECKERS = {
                        'hmin': lambda x: 0 <= x < self.hmax,
                        'hmax': lambda x: self.hmin < x <= 180,
                        'smin': lambda x: 0 <= x < self.smax,
                        'smax': lambda x: self.smin < x <= 255,
                        'vmin': lambda x: 0 <= x < self.vmax,
                        'vmax': lambda x: self.vmin < x <= 255
                    }

    def update(self, type_val, val):
        #print('Trying to update', type_val, val)
        if type_val in self.CHECKERS:
            if self.CHECKERS[type_val](val):
                setattr(self, type_val, val)
                self.show()

    def show(self):
        low = np.array([self.hmin, self.smin, self.vmin])
        high = np.array([self.hmax, self.smax, self.vmax])
        if self.img_hsv is not None:
            self.mask = cv2.inRange(self.img_hsv, low, high)
            to_show = cv2.bitwise_and(self.img, self.img, mask=self.mask)
            to_show = cv2.resize(to_show, dsize=(0, 0), fx=1/2, fy=1/2)
            to_show = np.hstack((cv2.resize(self.img, dsize=(0, 0), fx=1/2, fy=1/2), to_show))
            cv2.imshow(self.name, to_show)

    def new_img(self, filename):
        self.img = cv2.imread(filename)
        self.img_hsv = cv2.cvtColor(self.img, cv2.COLOR_BGR2HSV)

    def __str__(self):
        return '''\rH:  ({}-{})   S:  ({}-{})   V:  ({}-{})'''.format(
            self.hmin, self.hmax, self.smin, self.smax, self.vmin, self.vmax)


def the_key(filename, name='frame'):
    in_l = filename.rfind(name)
    in_r = filename.rfind('.')
    return int(filename[in_l + len(name):in_r])


c_filter = ColorFilter('Example')


def on_change(val, type_val, *args, **kwargs):
    global c_filter
    c_filter.update(type_val, val)


def main(path, fmt=None):
    if os.path.isfile(path):
        file_names = [path]
    else:
        file_names = sorted(glob.glob(path), key=partial(the_key, name=fmt))
    cv2.namedWindow('Example')
    cv2.createTrackbar('H min', 'Example', 0, 180, partial(on_change, type_val='hmin'))
    cv2.createTrackbar('H max', 'Example', 0, 180, partial(on_change, type_val='hmax'))
    cv2.setTrackbarPos('H max', 'Example', 180)
    cv2.createTrackbar('S min', 'Example', 0, 255, partial(on_change, type_val='smin'))
    cv2.createTrackbar('S max', 'Example', 0, 255, partial(on_change, type_val='smax'))
    cv2.setTrackbarPos('S max', 'Example', 255)
    cv2.createTrackbar('V min', 'Example', 0, 255, partial(on_change, type_val='vmin'))
    cv2.createTrackbar('V max', 'Example', 0, 255, partial(on_change, type_val='vmax'))
    cv2.setTrackbarPos('V max', 'Example', 255)

    for file_name in file_names:
        c_filter.new_img(file_name)
        while True:
            c_filter.show()
            sys.stdout.write(str(c_filter))
            k = cv2.waitKey(15)
            if k & 0xFF == ord('q'):
                sys.stdout.write('\n')
                sys.exit(0)
            elif k & 0xFF == ord('n'):
                break


if __name__ == '__main__':
    optional_name = sys.argv[2] if len(sys.argv > 2) else None
    main(sys.argv[1], optional_name)
