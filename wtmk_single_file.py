#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  wtmk_single_file.py
#  
#  Copyright 2018 Fabio Mazza <fabio@thinkless>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  
from PIL import Image,ExifTags
#from wtmk import parse_image
import os,traceback
import argparse
pad_fract = 0.05
logo_width_frac = 0.32
sufffolder = "processed"
defName = "image"
scaling = False
def main(args):
	
	valid_images = [".jpg",".gif",".png",".tga"]
	if(len(args)<3):
		print("You must insert the file and the watermark")
		return -1
	logo = Image.open(args[2])
	filename = args[1]
	if(len(args)>3):
		if (args[3] is "l") or (args[3] is "left"):
			right = False
		else:
			right = True
		if (args[3] is "t") or (args[3] is "top"):
			bottom = False
		else:
			bottom = True
	if(len(args)>4):
		if (args[4] is "t") or (args[4] is "top"):
			bottom = False
		else:
			bottom = True
	#for fiche in os.listdir(folder):
	#	ext = os.path.splitext(fiche)[1]
	#	if ext.lower() not in valid_images:
	#		continue
	parse_image(filename,logo,logo_width_frac,right,bottom)
	#if(len(args)<3):
	#	print("ERROR: Must supply the file to parse and the watermark")
	#	sys.exit(1)
	


	return 0

def parse_image(pathstring,logo,logo_wf,right=True,bottom=True):
	"""
	mark the image and save it
	"""
	imagename = os.path.basename(pathstring).split('.')[0]
	maindir = os.path.dirname(pathstring)

	print("Parsing image "+imagename+"...")
	image = correct_rotation(Image.open(pathstring))
	h = image.size[1]
	w = image.size[0]
	npix = h*w
	ratio = npix/6e6
	if(scaling and ratio>1):
		newimage = image.resize((int(w/ratio),int(h/ratio)))
	else:
		newimage = image
	#resize logo
	if newimage.width < newimage.height:
		logo_wf += 0.08
	newlogow = int(newimage.size[0]*logo_wf)
	newlogoh = int(float(logo.height)/logo.width*newlogow)
	print(h,w,npix,ratio)
	print(logo.size, newlogow,newlogoh)
	logonew = logo.resize((newlogow,newlogoh))
	padding = int(min(newimage.width,newimage.height)*pad_fract)+1
	if(right): posX = (newimage.width-newlogow-padding)
	else: posX = padding
	if(bottom): posY = (newimage.height-newlogoh-padding)
	else: posY = padding
	newimage.paste(logonew,(posX,posY),logonew)
	
	outfolder = os.path.join(maindir,sufffolder)

	
	count = 0
	filename = os.path.join(outfolder,"{}-{:03d}.jpg".format(imagename,count))
	while os.path.isfile(filename):
		count +=1
		filename = os.path.join(outfolder,"{}-{:03d}.jpg".format(imagename,count))
	directory = os.path.dirname(filename)

	if not os.path.exists(directory):
		os.makedirs(directory)
	newimage.save(filename)	

def correct_rotation(image):
	try:
		if hasattr(image, '_getexif'): # only present in JPEGs
			print("Found EXIF ROTATION DATA")
			for key in ExifTags.TAGS.keys(): 
				if ExifTags.TAGS[key]=='Orientation':
					break 
			e = image._getexif()       # returns None if no EXIF data
			if e is not None:
				exif=dict(e.items())
				orientation = exif[key]
				
				if orientation == 3:   image = image.rotate(180,expand=True)
				elif orientation == 6: image = image.rotate(270,expand=True)
				elif orientation == 8: image = image.rotate(90,expand=True)
				return image
		else:
			print("No EXIF Data")
	except:
		traceback.print_exc()
	return image
if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
