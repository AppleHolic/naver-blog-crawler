#! /usr/bin/python2.7
# -*-coding:utf-8-*-


import json
import os
import glob
import urllib2
import time

from bs4 import BeautifulSoup

from utils import checkdir, file_read, get_today_str, get_version


URLBASE = 'http://m.blog.naver.com/%s/%s'

def get_page(url):
    try:
        page = urllib2.urlopen(url, timeout=3)
        doc  = BeautifulSoup(page.read())
        return (doc, doc.find("div", {"class": "_postView"}))
    except Exception as e:
        print e, url
        time.sleep(100)
        return None

def make_structure(blog_id, log_no, raw, doc, crawled_time, crawler_version,
                                    title, written_time, url, tags, directory_seq,
                                    encoding='utf-8'):

    extract_crawlerTime  = get_today_str()
    extract_category     = lambda doc: doc.find("a", {"class": "_categoryName"}).get_text().encode(encoding)
    extract_content_html = lambda doc: doc.find("div", {"id": "viewTypeSelector"})

    def extract_sympathycount(doc):
        if doc.find("em", {"id": "sympathyCount"}) == None:
            return None
        else:
            return doc.find("em", {"id": "sympathyCount"}).get_text()

    def extract_images(htmls = extract_content_html(doc)):
        image_urls = []
        images = htmls.find_all("span", {"class":"_img _inl fx"})
        for i, image in enumerate(images):
            tmp = images[i]['thumburl'] + 'w2'
            image_urls.append(tmp)
        return image_urls

    return {u"blogId": blog_id,
            u"logNo": log_no,
            u"content": extract_content_html(doc).get_text().encode(encoding),
            u"contentHtml": str(extract_content_html(doc)),
            u"crawledTime": crawled_time,
            u"crawlerVersion": crawler_version,
            u"directorySeq": directory_seq,
            u"title": title,
            u"writtenTime": written_time,
            u"url": url,
            u"tags": tags,
            u"categoryName": extract_category(doc),
            u"sympathyCount": extract_sympathycount(doc),
            u"images": extract_images()}

def make_json(blog, blog_id, log_no, date, directory_seq, basedir, seconddir = "texts"):
    PATH = '%s/%02d/%02d' % (int(date[0:4]), int(date[5:7]), int(date[8:10]))
    targetpath = '%s/%s/%02d/%s' % (basedir, seconddir, directory_seq, PATH)
    checkdir(targetpath)
    filename = '%s/%s.json' % (targetpath, log_no)
    f        = open(filename, 'w')
    jsonstr  = json.dumps(blog, sort_keys=True, indent=4, encoding='utf-8')
    f.write(jsonstr)
    f.close()

def count_images(blog, directory_seq, basedir, seconddir = "logs"):
    targetpath = '%s/%s' % (basedir, seconddir)
    checkdir(targetpath)
    filename = '%s/count_images_%02d.txt' % (targetpath, directory_seq)
    f = open(filename, 'a')
    f.write(str(len(blog["images"]))+'\n')
    f.close()

def error_log_url(blog_id, log_no, date, directory_seq, basedir, seconddir = "logs"):
    targetpath = '%s/%s' % (basedir, seconddir)
    checkdir(targetpath)
    filename = '%s/error_url_%s-%02d-%02d.txt' % (targetpath, int(date[0:4]), int(date[5:7]), int(date[8:10]))
    f   = open(filename, 'a')
    url = '%s, http://m.blog.naver.com/%s/%s, access denied\n' % (directory_seq, blog_id, log_no)
    f.write(url)
    f.close()

def web_crawl(blog_id, log_no, crawled_time, crawler_version, title,
                        written_time, url, tags, date, directory_seq, basedir, debug=False):
    url = URLBASE % (blog_id, log_no)
    (raw, doc) = get_page(url)
    if doc != None:
        blog = make_structure(blog_id, log_no, raw, doc, crawled_time,
                        crawler_version, title, written_time, url, tags, directory_seq)
        count_images(blog, directory_seq, basedir)
        make_json(blog, blog_id, log_no, date, directory_seq, basedir)
    else:
        error_log_url(blog_id, log_no, date, directory_seq, basedir)

def return_information(directory_seq, basedir, date, crawler_version, seconddir ="lists", thirddir="texts", debug=False):
    if debug:
        print "Start blog text crawling..."
    directory_seq = int(directory_seq)
    try:
        targetpath = '%s/%s/%02d/%s/%02d/%02d'\
                         % (basedir, seconddir, directory_seq,\
                            int(date[0:4]), int(date[5:7]), int(date[8:10]))
    except TypeError as e:
        print e
        raise Exception('Please check input values (ex: the date)')
    itr1 = 0
    filenames = glob.glob('%s/*.json' % targetpath)
    for filename in filenames:
        print filename
        items = file_read(filename)
        itr2 = 0
        for i, blog in enumerate(items):
            try:
                check_targetpath = '%s/%s/%02d/%s/%02d/%02d'\
                                % (basedir, thirddir, directory_seq,\
                                   int(date[0:4]), int(date[5:7]), int(date[8:10]))
                check_filename = '%s.json' % (items[i]['logNo'])
                if not os.path.isfile('%s/%s' % (check_targetpath, check_filename)):
                    web_crawl(items[i]['blogId'],
                              items[i]['logNo'],
                              items[i]['crawledTime'],
                              crawler_version,
                              items[i]['title'],
                              items[i]['writtenTime'],
                              items[i]['url'],
                              items[i]['tags'],
                              date,
                              directory_seq,
                              basedir, debug=debug)
            except Exception as e:
                print e
            itr2 += 1
        if itr2 == len(items):
            print "%s items read completed successfully." % len(items)
        else:
            print "Not all items read."
        itr1 += 1
    if len(filenames) == itr1:
        print "%s files read completed successfully." % len(filenames)
        if len(filenames)==0:
            print "You probably have to crawl lists first."
    else:
        print "Not all files read."

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Get input parameters.',
                        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-c', '--category', required=True, dest='directory_seq',
                         help='assign target category to crawl')
    parser.add_argument('-p', '--path', dest='basedir',
                         help='assign data path')
    parser.add_argument('-d', '--date', dest='date',
                         help='assign date to crawl')
    parser.add_argument('-v', '--version', dest='version',
                         help='assign crawler version')
    parser.add_argument('--debug', dest='debug', action='store_true',
                         help='enable debug mode')
    args = parser.parse_args()

    if not args.basedir:
        args.basedir = './data'

    if not args.version:
        args.version = get_version()

    if args.debug:
        debug = True
    else:
        debug = False

    return_information(args.directory_seq, args.basedir, args.date, args.version, debug=debug)
