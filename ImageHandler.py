import datetime
import os
import requests
from PIL import Image
import tkinter as tk
import tkinter.messagebox


class ImageHandler:

    def __init__(self, start):
        self.start = start

    def create_img_dir(self):
        curdate_time = datetime.datetime.today().strftime("%Y%m%d_%Hh%Mm%Ss")
        # create new dir with timestamp as name
        if not os.path.exists('./downloads/'):
            try:
                os.mkdir('./downloads/')
            except OSError as e:
                tk.messagebox.showerror('System Error', 'Can not create directory\n\n' + str(e))
        try:
            new_dir = './downloads/' + curdate_time
            os.mkdir(new_dir)
        except OSError as e:
            tk.messagebox.showerror('System Error', 'Can not create directory\n\n' + str(e))
        return new_dir

    # downloads images, found in page and saved in images_links list
    # returns list that contains dir w/ images and list of images' names
    def download_images(self, img_dir, images_links):
        # curdate = datetime.date.today().strftime("%Y%m%d")
        curdate = datetime.datetime.today().strftime("%Y%m%d_%Hh%Mm%Ss")
        # create filename with current date as name
        filename = curdate + '-'
        ext = '.jpg'
        count = self.start

        # list of names of downloaded images
        img_names = []

        for url in images_links:
            try:
                image = requests.get(url)               # downloading file
            except requests.exceptions.SSLError as e:
                tk.messagebox.showerror('SSL Error', 'Can not load image ' + url + '\n\n' + str(e))
            except Exception as e:
                tk.messagebox.showerror('Unknown load image error', 'Can not load image ' + url + '\n\n' + str(e))
            num = "{0:0>3}".format(count)
            filename_full = filename + num + ext
            img_names.append(filename_full)         # add name to list of names

            with open(img_dir + '/' + filename_full, 'wb') as file:
                file.write(image.content)
            count += 1

        return img_names

    # open downloaded images and resize them to 800xN
    # 1st arg is dir w/ images, 2nd arg is list of images' names
    def img_resizer(self, img_dir, img_names, imgsize, m_imgsize):

        # create announcement image (always first on page so in list)
        try:
            main_img_name = img_names[0]
        except IndexError:
            print('no images')
            return
        anno_img = Image.open(img_dir + '/' + main_img_name)
        # img name (w/o extension) always 22 chars. Insert '-' in the end of the name to mark anno image
        main_img_name = main_img_name[:22] + '-' + main_img_name[22:]

        # if size !=0, do resize
        # for announce img resize only by width
        if m_imgsize != 0:
            basewidth = m_imgsize
            wpercent = (basewidth / float(anno_img.size[0])) # [0] is width [1] is height
            hsize = (float(anno_img.size[1]) * float(wpercent))
            hsize = int(round(hsize, 0))
            anno_img = anno_img.resize((basewidth, hsize), Image.ANTIALIAS)
        anno_img.save(img_dir + '/' + main_img_name)

        # resize images
        for img in img_names:
            cur_img = Image.open(img_dir + '/' + img)
            orig_width = cur_img.size[0]
            orig_height = cur_img.size[1]
            # if orig width of img >= orig height - change width
            if orig_width >= orig_height:
                # static width, change height
                # if base set as 0, leave orig size
                if imgsize != 0:
                    basewidth = imgsize
                else:
                    basewidth = orig_width
                # basewidth is x% of orig width
                wpercent = (basewidth / float(orig_width))
                # change orig height by x%
                hsize = (float(orig_height) * float(wpercent))
                hsize = int(round(hsize, 0))
                new_img = cur_img.resize((basewidth, hsize), Image.ANTIALIAS)
                new_img.save(img_dir + '/' + img)

            if orig_height > orig_width:
                # static height, change width
                # if base set as 0, leave orig size
                if imgsize != 0:
                    baseheight = imgsize
                else:
                    baseheight = baseheight = imgsize
                # baseheight is x% of orig height
                hpercent = (baseheight / float(orig_height))
                # change orig width by x%
                wsize = (float(orig_width) * float(hpercent))
                wsize = int(round(wsize, 0))
                new_img = cur_img.resize((wsize, baseheight), Image.ANTIALIAS)
                new_img.save(img_dir + '/' + img)
