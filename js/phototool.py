#!/usr/bin/env python
# -*- coding:utf8  -*-

import os
import glob
from PIL import Image, ExifTags
import json

config = {
        # github 存储图片的仓库（本地仓库基准目录）
        'github_img_host_base': '/Users/smaug/blogimg_2',
        # 会对这个目录下的所有文件夹进行遍历，相同目录生成_samll 的 缩略图
        'img_path':             '/Users/smaug/blogimg_2/rebootcat/photowall',
        # cdn 前缀
        'cdn_url_prefix':       'https://cdn.jsdelivr.net/gh/smaugx/MyblogImgHosting_2',
        # hexo 博客存放 photos 信息的 json 文件
        'photo_info_json':      '/Users/smaug/blog_rebootcat/source/photos/photoslist.json',
        }

# 压缩图片到 90%(目的是为了移除一些gps 等信息，并非真的为了压缩）
def compress_img(img_path, rate = 0.99, override = False):
    support_ftype_list = ['png', 'PNG', 'jpeg', 'JPEG', 'gif', 'GIF', 'bmp']
    sp_img = img_path.split('.')
    if not sp_img or sp_img[-1] not in support_ftype_list:
        print("not support image type:{0}", img_path)
        return False
    sp_img = img_path.split('/')
    if not sp_img:
        print("please give the right image path:{0}", img_path)
        return False
    img_full_name = sp_img[-1]
    img_name = img_full_name.split('.')[0]
    img_type = img_full_name.split('.')[1]
    img_path_prefix = img_path[:-len(img_full_name)]
    
    # 覆盖原图或者另存为
    compress_img_path = ''
    if override:
        compress_img_path = img_path
    else:
        compress_img_path = '{0}{1}_com.{2}'.format(img_path_prefix, img_name, img_type)

    img = Image.open(img_path)
    try:
        for orientation in ExifTags.TAGS.keys() : 
            if ExifTags.TAGS[orientation]=='Orientation' : break 
        exif=dict(img._getexif().items())
        if   exif[orientation] == 3 : 
            img=img.rotate(180, expand = True)
        elif exif[orientation] == 6 : 
            img=img.rotate(270, expand = True)
        elif exif[orientation] == 8 : 
            img=img.rotate(90, expand = True)
    except Exception as e:
        print("catch exception:{0}",e)

    try:
        original_size = img.size
        length = original_size[0]
        height = original_size[1]
        new_length = int(length * rate)
        new_height = int(height * rate)
        print("originla length:{0} height:{1}", length, height)
        print("after compress length:{0} height:{1}", new_length, new_height)
        img = img.resize((new_length, new_height), Image.ANTIALIAS)
        img.save(compress_img_path, img_type)
        print("save compress img {0}".format(compress_img_path))
        return True
    except Exception as e:
        print("catch exception:{0}",e)

    return False


# 对 img_path 目录下的文件夹递归生成缩略图保存到同目录下
def thumbnail_pic(github_img_host_base, img_path, cdn_url_prefix):
    # 删除最后一个 '/'
    if img_path[-1] == '/':
        img_path = img_path[:-1]
    if github_img_host_base[-1] == '/':
        github_img_host_base = github_img_host_base[:-1]
    if cdn_url_prefix[-1] == '/':
        cdn_url_prefix = cdn_url_prefix[:-1]

    photo_info_list = []

    for item in os.listdir(img_path):
        print(item)
        abs_item = os.path.join(img_path, item)
        if os.path.isdir(abs_item): # sub-dir
            sub_img_path = abs_item
            print("cd dir:{0}".format(sub_img_path))
            sub_photo_info_list = thumbnail_pic(github_img_host_base, sub_img_path, cdn_url_prefix)
            photo_info_list.extend(sub_photo_info_list)
        else: # file
            ftype = item.split('.')
            if not ftype or len(ftype) != 2:
                print("error: invalid file:{0}".format(item))
                continue
            fname = ftype[0]  # a.png -> a
            ftype = ftype[1]  # a.png -> png
            support_ftype_list = ['png', 'PNG', 'jpeg', 'JPEG', 'gif', 'GIF', 'bmp']
            if ftype not in support_ftype_list:
                print("error: file type {0} not support, only support {1}".format(ftype, json.dumps(support_ftype_list)))
                continue

            abs_file = abs_item
            if item.find('_small') != -1: # 这是缩略图
                continue
            small_file = '{0}_small.{1}'.format(fname, ftype)
            abs_small_file = os.path.join(img_path, small_file)  # 缩略图绝对路径
            if os.path.exists(abs_small_file):
                # 对应的 _small 缩略图已经存在
                continue
            
            compress_status = compress_img(abs_file, 0.9, True)
            if not compress_status:
                print("compress_img fail:{0}", abs_file)
                continue

            im = Image.open(abs_file)
            original_size = im.size
            length = original_size[0]
            height = original_size[1]
            m = int(float(length) / 200.0)  # 计算缩小比例 (缩略图限制 200 长度)
            new_length = int(float(length) / m)
            new_height = int(float(height) / m)
            im.thumbnail((new_length, new_height))  # 生成缩略图
            im.save(abs_small_file, ftype)  # 保存缩略图
            print("save thumbnail img {0}".format(abs_small_file))

            relative_file       = abs_file[len(github_img_host_base) + 1:] # 计算相对路径，用来拼接 cdn
            relative_small_file = abs_small_file[len(github_img_host_base) + 1:] 

            cdn_url_file        = '{0}/{1}'.format(cdn_url_prefix, relative_file) 
            cdn_url_small_file  = '{0}/{1}'.format(cdn_url_prefix, relative_small_file) 

            # 格式: 690.690;8.png;http://cdn_file_url;http://cdn_small_file_url;
            line = '{0}.{1};{2};{3};{4}'.format(length, height, item, cdn_url_file, cdn_url_small_file)
            photo_info_list.append(line)

    # end for loop
    print('dir:{0} Done!'.format(img_path))
    return photo_info_list


if __name__=='__main__':
    github_img_host_base = config.get('github_img_host_base')
    img_path             = config.get('img_path')
    cdn_url_prefix       = config.get('cdn_url_prefix')
    photo_info_json      = config.get('photo_info_json')

    photo_info_list     = []
    photo_info_list_has = []
    photo_info_list = thumbnail_pic(github_img_host_base, img_path, cdn_url_prefix)

    if os.path.exists(photo_info_json):
        with open(photo_info_json, 'r') as fin:
            photo_info_list_has = json.loads(fin.read())
            fin.close()

    photo_info_list_has.extend(photo_info_list)  # 追加此次新增的 photo info

    with open(photo_info_json, 'w') as fout:
        fout.write(json.dumps(photo_info_list_has, indent = 2))
        print("save photo_info_list to {0}".format(photo_info_json))
        fout.close()

    print("\nAll Done")
