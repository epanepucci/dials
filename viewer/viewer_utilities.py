#
#  viewer_utilities.py
#
#  Copyright (C) 2014 Diamond Light Source
#
#  Author: Luis Fuentes-Montero (Luiso)
#
#  This code is distributed under the BSD license, a copy of which is
#  included in the root directory of this package.

import numpy, wx
import matplotlib.pyplot as plt
def GetBitmap_from_np_array(np_img_2d, Intst_max, img_scale):
  fig = plt.figure()
  # remember to make sure this is our convention in (x, y) vs (row, col)
  if Intst_max > 0:
    plt.imshow(numpy.transpose(np_img_2d), interpolation = "nearest", vmin = 0, vmax = Intst_max)


  else:
    plt.imshow(numpy.transpose(np_img_2d), interpolation = "nearest", vmin = 0, vmax = 10)


  ax = fig.add_subplot(1,1,1)
  #ax.plot([1, 2, 3, 4], [10, 20, 25, 30])
  #set_default_intervals()
  #ax.xaxis.set_data_interval(vmin = 2, vmax = 4, ignore=False)
  dat = ax.xaxis.get_ticklabels()
  for dat_prnt in dat:
    print "ax.xaxis.get_ticklabels() =", dat_prnt
  ax.xaxis.set_ticklabels(["foo" , "bar", "ouch"])



  fig.canvas.draw()
  width, height = fig.canvas.get_width_height()
  np_buf = numpy.fromstring ( fig.canvas.tostring_rgb(), dtype=numpy.uint8 )
  np_buf.shape = (width, height, 3)
  np_buf = numpy.roll(np_buf, 3, axis = 2)
  image = wx.EmptyImage(width, height)
  image.SetData( np_buf )


  return image, width, height

def from_wx_image_to_wx_bitmap(wx_image, width, height, scale):
  NewW = int(width * scale)
  NewH = int(height * scale)
  wx_image = wx_image.Scale(NewW, NewH, wx.IMAGE_QUALITY_HIGH)

  #image.SetData( np_buf.tostring()) # looks like there is no need to convert
  wxBitmap = wx_image.ConvertToBitmap()
  return wxBitmap


def build_np_img(width = 64, height = 64):
  data2d = numpy.zeros( (width, height), 'float')
  for x in range(0, width):
    for y in range(0, height):
      data2d[x,y] = x + y
  data2d[width/4:width*3/4,height/4:height*3/4] = 0

  return data2d
