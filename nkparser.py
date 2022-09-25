import json
import re
import requests
import datetime
import tkinter as tk
import tkinter.messagebox
from bs4 import BeautifulSoup, Comment

from ImageHandler import ImageHandler


class MyParser:

    def __init__(self, url, start, source_rb, chbx, imgsize):
        self.url = url
        self.start = start
        self.source_rb = source_rb
        self.chbx = chbx
        self.imgsize = imgsize
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64)'
                                 ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'}

        try:
            with open('config.json', 'r', encoding='utf-8') as cfg_file:
                config = json.load(cfg_file)
                config = config['sites'][self.source_rb]
        except EnvironmentError as e:
            tk.messagebox.showerror('File open error', 'Can not open config file:  \n\n' + str(e))

        try:
            self.page = requests.get(url, headers=headers)
            # catches http error status codes 4xx-5xx
            self.page.raise_for_status()
        except requests.exceptions.InvalidURL as e:
            tk.messagebox.showerror('Invalid URL', str(e))
        except requests.exceptions.MissingSchema as e:
            tk.messagebox.showerror('Missing Schema Error', str(e))
            # self.error = 'Missing Schema error: ' + str(e)
        except requests.exceptions.ConnectionError as e:
            tk.messagebox.showerror('Connection Error', 'Can not connect to ' + self.url + '\n\n' + str(e))
        except requests.exceptions.HTTPError as e:
            tk.messagebox.showerror('HTTP Error', 'Can not load page ' + self.url + '\n\n' + str(e))

        self.soup = BeautifulSoup(self.page.text, 'html.parser')

        self.source = config['source']

        self.title_tag = config['title_tag']
        self.title_attr = config['title_attr']
        self.title_attr_name = config['title_attr_name']

        self.article_tag = config['article_tag']
        self.article_attr = config['article_attr']
        self.article_attr_name = config['article_attr_name']

        self.adv_blocks = config['adv_blocks']
        self.tags_to_remove = config['tags_to_remove']

        self.main_img_tag = config['main_img_tag']
        self.main_img_attr = config['main_img_attr']
        self.main_img_attr_name = config['main_img_attr_name']
        self.main_img_img_class = config['main_img_img_class']

    def get_title(self):
        title = self.soup.find(self.title_tag, {self.title_attr: self.title_attr_name})
        if title is None:
            return 'No title tags found. Maybe they was changed.'
        title_str = title.string
        # fix caps in radio title
        if self.source_rb == 1:
            title_str = title_str.lower().capitalize()
        return title_str

    # if return_as_obj is True, returns bsoup object, if False, returns plain text
    def get_article(self, return_as_obj=False):
        article = self.soup.find(self.article_tag, {self.article_attr: self.article_attr_name})

        if return_as_obj:
            return article

        if article is None:
            return 'No articles tags found. Maybe they was changed.'
        # remove html comments
        for child in article:
            if isinstance(child, Comment):
                child.extract()
        # remove bottom ad blocks with listed classes and script tag
        bad_tags = []
        for tag in self.tags_to_remove:
            bad_tags += article.find_all(tag)
        for tag in bad_tags:
            try:
                tag.decompose()
            except AttributeError:
                pass
        for i in self.adv_blocks:
            try:
                useless = article.find(class_=i)
                # removes tag from html tree
                useless.decompose()
            except AttributeError:
                pass
        imgs = self.get_images(True)
        new_article = ''
        # starts from 1 because announce image is 0 element
        img_counter = self.start + 1
        imgtag = re.compile('<img.*?>')
        for line in article:
            if re.search(imgtag, str(line)):
                new_article += self.get_img_links(img_counter, img_counter)
                img_counter += 1
                continue
            new_article += str(line)
        # gets plain text without tags
        # article = article.get_text()
        new_article = new_article.strip()
        # clean tags
        # new_article = re.sub(r'(((?<=<div)|(?<=<p)) .*?(?=>))', '', new_article, flags=re.DOTALL)
        # new_article = re.sub(r'<iframe.*?</iframe>', '', new_article, flags=re.DOTALL)
        # remove 3 and more newlines
        new_article = re.sub(r'\n{3,}', '\n\n', new_article, flags=re.DOTALL)
        # replace div with p
        new_article = new_article.replace('div>', 'p>')
        # remove empty p
        new_article = re.sub(r'(<p>(\s)*</p>)|(<p>(\n)*</p>)', '', new_article, flags=re.DOTALL)
        # replace strong tag with b
        # new_article = new_article.replace('strong>', 'b>')
        # replace newlines with <br>
        # article = article.replace('\n', '<br>')
        # return article
        return new_article

    def get_author(self):
        author = '\n\n<p>Матеріали сайту <a target="_blank" href="' + self.url + '"> &laquo;' + self.source + '&raquo;</a></p>'
        return author

    # generates links for images
    def get_img_links(self, start, end):
        curyear = datetime.date.today().strftime("%Y")
        curmonth = datetime.date.today().strftime("%m")
        curdate = datetime.date.today().strftime("%Y%m%d")
        if self.chbx == 1:
            startstr = '\n<img width="100" height="100" src="./uploaded/'
        else:
            startstr = '\n<img src="./images/' + curyear + '/' + curmonth + '/'
        result = ''
        if not start:
            start = self.start
        count = start
        # for n in range(count, end + count):
        for n in range(count, end + 1):
            num = "{0:0>3}".format(n)
            result += startstr + curdate + '-' + num + '.jpg" title="" vspace="4">'

        if self.chbx == 1:
            return '\n<p style="text-align:center">' + result + '</p>\n'
        else:
            return '\n<center>' + result + '\n</center>\n'

    # if links_only=True returns list with src of images
    # otherwise returns string with prepared links
    def get_images(self, links_only=False):
        images_links = []
        article = self.get_article(True)

        # get main image
        try:
            main_img_list = self.soup.find(self.main_img_tag, {self.main_img_attr: self.main_img_attr_name})
            main_img_list = main_img_list.select('img.'+self.main_img_img_class)
            for tag in main_img_list:
                if 'lazyload' not in tag.attrs['class']:
                    main_img = tag
            main_img = main_img.get('src')
        except Exception as e:
            tk.messagebox.showerror('Announce image find error', 'Can not find main image ' + '\n\n' + str(e))
        # check if img is .jpg
        if main_img[-3:] == 'jpg' or main_img[-4:] == 'jpeg':
            images_links.append(main_img)

        # get all news images links
        images_list = article.find_all('img')  # selects all <img> as list
        for link in images_list:
            link = link.get('src')
            if link[-3:] == 'jpg' or link[-4:] == 'jpeg':
                images_links.append(link)
        if links_only:
            return images_links

        # download images and get prepared img links
        imager = ImageHandler(self.start)
        img_dir = imager.create_img_dir()
        img_names = imager.download_images(img_dir, images_links)
        imager.img_resizer(img_dir, img_names, self.imgsize)

        prepared_links = self.get_img_links(False, len(images_links))
        return prepared_links

    def get_video(self):
        video_links = []
        article = self.get_article(True)
        # get all video links
        video_list = article.find_all('iframe')  # selects all <iframe> as list
        if not video_list:
            return ''

        for link in video_list:
            try:
                vid_init_width = int(re.search(r'width="(\d+)"', str(link)).group(1))
            except (AttributeError, ValueError):
                vid_init_width = 560
            try:
                vid_init_height = int(re.search(r'height="(\d+)"', str(link)).group(1))
            except (AttributeError, ValueError):
                vid_init_height = 315
            vid_width = 800
            coeff = round(vid_width / vid_init_width, 2)
            vid_height = int(vid_init_height * coeff)

            link_src = link.get('data-src')
            if not link_src:
                link_src = link.get('src')
            if 'youtube.com' in link_src:
                video_links.append(link_src)

        formatted_video_links = []
        for link in video_links:
            formatted_link = '<iframe width="{0}" height="{1}" src="{2}" frameborder="0" gesture="media" \
allow="encrypted-media" allowfullscreen="allowfullscreen"></iframe>'.format(vid_width, vid_height, link)
            formatted_video_links.append(formatted_link)
        ready_links = '\n<br><br>'.join(formatted_video_links)
        return '\n<center>\n' + ready_links + '\n</center>'
