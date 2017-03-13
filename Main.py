import urllib.request
import urllib.parse
import urllib.error
import json
import time
import datetime
from tkinter import *
from tkinter import ttk
import threading


def common_request_maker(path):
    if path:
        req = urllib.request.Request(path)
        req.add_header('User-Agent',
                       'Mozilla/5.0 (Linux; Android 4.4.4; Samsung Galaxy S4 - 4.4.4 - API 19 - 1080x1920 Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/33.0.0.0 Mobile Safari/537.36')
        req.add_header('X-Requested-With', 'com.android.browser')
        return req
    else:
        return None


# https://passport.weibo.cn/sso/login
# 微博登陆
def weibo_login(name, passwd):
    if name and passwd:
        req = common_request_maker('https://passport.weibo.cn/sso/login')
        req.add_header('Origin', 'https://passport.weibo.cn')
        req.add_header('Referer', 'https://passport.weibo.cn/signin/login?entry=mweibo')
        data = urllib.parse.urlencode({'username': name,
                                       'password': passwd})  # + '&savestate=1&r=http://m.weibo.cn/?jumpfrom=weibocom&entry=mweibo&mainpageflag=1&ec=0'
        log(data)
        data = bytes(data, 'utf-8')
        # request.add_header('Content-Length', len(data))
        try:
            response = urllib.request.urlopen(req, data, timeout=10)
        except urllib.error.HTTPError as e:
            log(e)
            return
        res_str = str(response.read(), 'utf-8')
        log('登陆返回内容-----------')
        log(res_str)
        log('登陆返回内容-----------')
        login_data = None
        try:
            res_obj = json.loads(res_str)
            if res_obj and res_obj.get('retcode') == 20000000:
                login_data = {}
                login_data['data'] = res_obj
                login_data['uid'] = res_obj.get('data').get('uid')
                login_data['loginresulturl_ticket'] = \
                    urllib.parse.parse_qs(urllib.parse.urlparse(res_obj.get('data').get('loginresulturl')).query)[
                        'ticket']
                login_data['cookie'] = str(response.getheader('Set-Cookie'))
                login_data['weibo_ticket'] = urllib.parse.parse_qs(
                    urllib.parse.urlparse(res_obj.get('data').get('crossdomainlist').get('weibo.com')).query)['ticket']
                login_data['sina_ticket'] = urllib.parse.parse_qs(
                    urllib.parse.urlparse(res_obj.get('data').get('crossdomainlist').get('sina.com.cn')).query)[
                    'ticket']
                # login_data['st'] = weibo_login_st(login_data['cookie'])
                # log(login_data['st'])
            else:
                assert BaseException('登录失败!')

        except BaseException as e:
            log(e)

        return login_data


# http://m.weibo.cn/mblog
# 拿一个叫st的东西不知道是啥,但是后面有些接口会校验,这里图方便直接定死去找,按理说应该用正则
# 后来发现要用的时候还得在查。。。先搁置
def weibo_login_st(cookie):
    req = common_request_maker('http://m.weibo.cn/mblog')
    req.add_header('Referer', 'https://passport.weibo.cn/signin/login?entry=mweibo')
    req.add_header('Cookie', cookie)
    try:
        response = urllib.request.urlopen(req, timeout=10)
    except urllib.error.HTTPError as e:
        log(e)
        return
    res_str = str(response.read(), 'utf-8')
    log('weibo_login_st返回内容-----------')
    log(res_str)
    log('weibo_login_st返回内容-----------')
    index = res_str.find('"st":"')
    return res_str[index + 6:index + 12]


# http://m.weibo.cn/feed/friends?version=v4
# 获取微博首页next_cursor是用来翻页的,第一页不传就好
def weibo_homepage(login_data, next_cursor=None):
    if next_cursor:
        req = common_request_maker('http://m.weibo.cn/feed/friends?version=v4&next_cursor=' + next_cursor)
    else:
        req = common_request_maker('http://m.weibo.cn/feed/friends?version=v4')
    req.add_header('Referer', 'http://m.weibo.cn/?jumpfrom=wapv4')
    req.add_header('Cookie', login_data['cookie'])

    try:
        response = urllib.request.urlopen(req, timeout=10)
    except urllib.error.HTTPError as e:
        log(e)
        return
    res_str = str(response.read(), 'utf-8')
    log('获取首页返回内容-----------')
    log(res_str)
    log('获取首页返回内容-----------')

    try:
        res_obj = json.loads(res_str)
        res_obj = res_obj[0]
        log(res_obj.get('next_cursor'))

        return res_obj['card_group']


    except BaseException as e:
        log(e)


'''
[{
	"mod_type": "mod\/pagelist",
	"maxPage": 50,
	"page": 1,
	"url": "\/feed\/friends?version=v4",
	"previous_cursor": 4084741676406768,
	"next_cursor": 4084627146862544,
	"loadMore": false,
	"card_group": [{
		"card_type": 9,
		"mblog": {
			"created_at": "\u4eca\u5929 07:36",
			"id": "4084741676406768",
			"mid": "4084741676406768",
			"idstr": "4084741676406768",
			"text": "<a class='k' href='http:\/\/m.weibo.cn\/k\/\u4e07\u8c61?from=feed'>#\u4e07\u8c61#<\/a>\u3010\u5973\u5b50\u5361\u91cc\u7a81\u7136\u591a\u51fa7\u4e07\u5143 \u4e00\u4e2a\u591a\u6708\u65e0\u4eba\u95ee<span class=\"iconimg iconimg-xs\"><img src=\"\/\/h5.sinaimg.cn\/m\/emoticon\/icon\/default\/d_chijing-f4f9e95da7.png\" style=\"width:1em;height:1em;;\"><\/span>\u3011\u5361\u91cc\u7a81\u7136\u8f6c\u51657\u4e07\u5143\u94b1\uff0c\u8d75\u5973\u58eb\u4e00\u5f00\u59cb\u89c9\u5f97\u662f\u9a97\u5c40\uff0c\u540e\u6765\u53d1\u73b0\u786e\u5b9e\u5165\u8d26\u4e86\uff0c\u53c8\u60f3\u7740\u5feb\u70b9\u627e\u5230\u5931\u4e3b\u3002\u201c\u4e0d\u662f\u81ea\u5df1\u7684\u94b1\uff0c\u5fc3\u91cc\u603b\u662f\u4e2a\u4e8b\u201d\uff0c\u8d75\u5973\u58eb\u8bf4\uff0c\u5979\u5f53\u65f6\u5c31\u7ed9\u94f6\u884c\u5ba2\u670d\u6253\u4e86\u7535\u8bdd\uff0c\u4f46\u5ba2\u670d\u4eba\u5458\u79f0\u67e5\u4e0d\u5230\u5b58\u5165\u4eba\u7684\u4fe1\u606f\u3002<a data-url=\"http:\/\/t.cn\/RimmY2C\" target=\"_blank\" href=\"http:\/\/weibo.cn\/sinaurl?wm=3049_0022&from=qudao&luicode=20000174&featurecode=20000180&u=http%3A%2F%2Fnews.sina.com.cn%2Fo%2F2017-03-13%2Fdoc-ifychihc6312399.shtml%3Fwm%3D3049_0022%26from%3Dqudao\" class=\"\"><span class=\"iconimg iconimg-xs\"><img src=\"\/\/h5.sinaimg.cn\/upload\/2015\/09\/25\/3\/timeline_card_small_web_default.png\"><\/span><\/i><span class=\"surl-text\">\u5973\u5b50\u5361\u91cc\u591a7\u4e07.1\u4e2a\u591a\u6708\u65e0\u4eba\u95ee<\/a> \u200b",
			"textLength": 258,
			"source_allowclick": 0,
			"source_type": 1,
			"source": "\u5fae\u535a weibo.com",
			"appid": 780,
			"favorited": false,
			"truncated": false,
			"in_reply_to_status_id": "",
			"in_reply_to_user_id": "",
			"in_reply_to_screen_name": "",
			"pic_ids": ["60718250ly1fdkv7l8496j20go0goad9"],
			"thumbnail_pic": "http:\/\/wx3.sinaimg.cn\/thumbnail\/60718250ly1fdkv7l8496j20go0goad9.jpg",
			"bmiddle_pic": "http:\/\/wx3.sinaimg.cn\/bmiddle\/60718250ly1fdkv7l8496j20go0goad9.jpg",
			"original_pic": "http:\/\/wx3.sinaimg.cn\/large\/60718250ly1fdkv7l8496j20go0goad9.jpg",
			"geo": null,
			"user": {
				"id": 1618051664,
				"screen_name": "\u5934\u6761\u65b0\u95fb",
				"profile_image_url": "http:\/\/tva4.sinaimg.cn\/crop.25.38.540.540.180\/60718250jw8fcz2lmdjz5j20go0got9k.jpg",
				"profile_url": "http:\/\/m.weibo.cn\/u\/1618051664?uid=1618051664&luicode=20000174&featurecode=20000180",
				"statuses_count": 122192,
				"verified": true,
				"verified_type": 3,
				"verified_type_ext": 0,
				"verified_reason": "\u65b0\u6d6a\u65b0\u95fb\u4e2d\u5fc324\u5c0f\u65f6\u64ad\u62a5\u5168\u7403\u91cd\u5927\u65b0\u95fb",
				"description": "\u6bcf\u65e5\u64ad\u62a5\u5168\u7403\u5404\u7c7b\u91cd\u8981\u8d44\u8baf\u3001\u7a81\u53d1\u65b0\u95fb\uff0c\u5168\u592924\u5c0f\u65f6\u5373\u65f6\u53d1\u5e03\u3002\u6b22\u8fce\u62a5\u6599\u3001\u6295\u7a3f\uff0c\u8bf7\u53d1\u79c1\u4fe1\u6216\u8005\u90ae\u4ef6\uff1axlttnews@vip.sina.com\u3002",
				"gender": "f",
				"mbtype": 2,
				"urank": 41,
				"mbrank": 4,
				"follow_me": false,
				"following": true,
				"followers_count": 51613780,
				"follow_count": 836,
				"cover_image_phone": "http:\/\/ww1.sinaimg.cn\/crop.0.0.640.640.640\/9d44112bjw1f1xl1c10tuj20hs0hs0tw.jpg"
			},
			"reposts_count": 249,
			"comments_count": 819,
			"attitudes_count": 936,
			"isLongText": false,
			"mlevel": 0,
			"visible": {
				"type": 0,
				"list_id": 0
			},
			"biz_ids": [0],
			"biz_feature": 0,
			"page_type": 32,
			"hasActionTypeCard": 0,
			"darwin_tags": [],
			"hot_weibo_tags": [],
			"text_tag_tips": [],
			"rid": "0_0_1_2775502175666427315",
			"userType": 0,
			"positive_recom_flag": 0,
			"gif_ids": "",
			"is_show_bulletin": 2,
			"url_struct": [{
				"url_title": "\u5973\u5b50\u5361\u91cc\u591a7\u4e07.1\u4e2a\u591a\u6708\u65e0\u4eba\u95ee",
				"url_type_pic": "http:\/\/h5.sinaimg.cn\/upload\/2015\/09\/25\/3\/timeline_card_small_web_default.png",
				"url_long": "http:\/\/news.sina.com.cn\/o\/2017-03-13\/doc-ifychihc6312399.shtml?wm=3049_0022&from=qudao",
				"url_short": "http:\/\/t.cn\/RimmY2C",
				"url_ori": "http:\/\/t.cn\/RimmY2C"
			}],
			"page_info": {
				"object_type": "webpage",
				"type": 2,
				"page_pic": "http:\/\/ww1.sinaimg.cn\/thumbnail\/dbc0ba47jw1f1a9zsl17fj2050050q2t.jpg",
				"page_url": "http:\/\/weibo.cn\/sinaurl?url=http%3A%2F%2Fnews.sina.com.cn%2Fo%2F2017-03-13%2Fdoc-ifychihc6312399.shtml%3Fwm%3D3049_0022%26from%3Dqudao&luicode=20000174&featurecode=20000180&u=http%3A%2F%2Fweibo.cn%2Fsinaurl%3Furl%3Dhttp%253A%252F%252Fnews.sina.com.cn%252Fo%252F2017-03-13%252Fdoc-ifychihc6312399.shtml%253Fwm%253D3049_0022%2526from%253Dqudao%26luicode%3D20000174%26featurecode%3D20000180%26u%3Dhttp%253A%252F%252Ffeed.mix.sina.com.cn%252Flink_card%252Fredirect%253Furl%253Dhttp%25253A%25252F%25252Fnews.sina.com.cn%25252Fo%25252F2017-03-13%25252Fdoc-ifychihc6312399.shtml%25253Fwm%25253D3049_0022%252526from%25253Dqudao",
				"content1": "\u5973\u5b50\u5361\u91cc\u591a7\u4e07.1\u4e2a\u591a\u6708\u65e0\u4eba\u95ee",
				"content2": "\u539f\u6807\u9898\uff1a\u5361\u91cc\u7a81\u7136\u591a7\u4e07 \u4e00\u4e2a\u591a\u6708\u6ca1\u4eba\u95ee \u5361\u91cc\u7a81\u7136\u8f6c\u51657\u4e07\u5143\u94b1\uff0c\u8d75\u5973\u58eb\u4e00\u5f00\u59cb\u89c9\u5f97\u662f\u9a97\u5c40\uff0c\u540e\u6765\u53d1\u73b0\u786e\u5b9e\u5165\u8d26\u4e86\uff0c\u53c8\u60f3\u7740\u5feb\u70b9\u627e\u5230\u5931\u4e3b\u3002",
				"page_desc": "\u539f\u6807\u9898\uff1a\u5361\u91cc\u7a81\u7136\u591a7\u4e07 \u4e00\u4e2a\u591a\u6708\u6ca1\u4eba\u95ee \u5361\u91cc\u7a81\u7136\u8f6c\u51657\u4e07\u5143\u94b1\uff0c\u8d75\u5973\u58eb\u4e00\u5f00\u59cb\u89c9\u5f97\u662f\u9a97\u5c40\uff0c\u540e\u6765\u53d1\u73b0\u786e\u5b9e\u5165\u8d26\u4e86\uff0c\u53c8\u60f3\u7740\u5feb\u70b9\u627e\u5230\u5931\u4e3b\u3002",
				"pic_info": {
					"pic_big": {
						"url": "http:\/\/ww1.sinaimg.cn\/thumbnail\/dbc0ba47jw1f1a9zsl17fj2050050q2t.jpg"
					}
				}
			},
			"pics": [{
				"pid": "60718250ly1fdkv7l8496j20go0goad9",
				"url": "http:\/\/wx3.sinaimg.cn\/thumb180\/60718250ly1fdkv7l8496j20go0goad9.jpg",
				"size": "thumb180",
				"geo": {
					"width": 180,
					"height": 180,
					"croped": false
				},
				"large": {
					"size": "large",
					"url": "http:\/\/wx3.sinaimg.cn\/large\/60718250ly1fdkv7l8496j20go0goad9.jpg",
					"geo": {
						"width": "600",
						"height": "600",
						"croped": false
					}
				}
			}],
			"bid": "Ezyw7qSGY"
		}
	}, {
		"card_type": 9,
		"mblog": {
'''


# http://m.weibo.cn/index/my?format=cards
# 微博获取首页自己发的帖子(准备拿来删除用的)
def weibo_get_my_posts(login_data, page=None):
    if page:
        req = common_request_maker('http://m.weibo.cn/index/my?format=cards&page=2' + page)
    else:
        req = common_request_maker('http://m.weibo.cn/index/my?format=cards')
    req.add_header('Cookie', login_data['cookie'])

    try:
        response = urllib.request.urlopen(req, timeout=10)
    except urllib.error.HTTPError as e:
        log(e)
        return
    res_str = str(response.read(), 'utf-8')
    log('获取自己发的帖子 返回内容-----------')
    log(res_str)
    log('获取自己发的帖子 返回内容-----------')

    try:
        res_obj = json.loads(res_str)
        res_obj = res_obj[0]
        posts = res_obj['card_group']

        log(posts[0]['mblog']['id'])

        return posts[0]['mblog']['id']

    except BaseException as e:
        log(e)


'''
[{
	"mod_type": "mod\/pagelist",
	"maxPage": 6,
	"page": 1,
	"url": "\/index\/my?format=cards",
	"previous_cursor": 0,
	"next_cursor": 0,
	"loadMore": false,
	"card_group": [{
		"card_type": 9,
		"mblog": {
			"created_at": "1\u5206\u949f\u524d",
			"id": 4084807677386668,
			"mid": "4084807677386668",
			"idstr": "4084807677386668",
			"text": "123abc \u200b\u200b\u200b",
			"textLength": 6,
			"source_allowclick": 0,
			"source_type": 1,
			"source": "\u624b\u673a\u5fae\u535a\u89e6\u5c4f\u7248",
			"appid": 365550,
			"favorited": false,
			"pic_ids": [],
			"user": {
				"id": 2351382613,
				"screen_name": "m18845741254258789",
				"profile_image_url": "http:\/\/tvax1.sinaimg.cn\/crop.0.0.224.224.180\/8c274055ly1fcn5f1ue8mj2069069q3i.jpg",
				"profile_url": "\/u\/2351382613",
				"statuses_count": 10,
				"verified": false,
				"verified_reason": "",
				"description": "1000\u7c89\uff0c\u4ec55\u6bdb\u3002\u4e13\u4e1a\u670d\u52a1\u503c\u5f97\u4fe1\u8d56",
				"remark": "",
				"verified_type": -1,
				"gender": "m",
				"mbtype": 0,
				"h5icon": {
					"main": 0,
					"other": []
				},
				"ismember": 0,
				"valid": null,
				"fansNum": 100,
				"follow_me": false,
				"following": false
			},
			"reposts_count": 0,
			"comments_count": 0,
			"attitudes_count": 0,
			"isLongText": false,
			"mlevel": 0,
			"visible": {
				"type": 0,
				"list_id": 0
			},
			"biz_feature": 0,
			"hasActionTypeCard": 0,
			"hot_weibo_tags": [],
			"text_tag_tips": [],
			"userType": 0,
			"positive_recom_flag": 0,
			"gif_ids": "",
			"is_show_bulletin": 2,
			"created_timestamp": 1489377506,
			"bid": "EzAezuZBO",
			"like_count": 0,
			"attitudes_status": 0
		}
	}, {
		"card_type": 9,
		"mblog": {
			"created_at": "21\u5206\u949f\u524d",
			"id": 4084802572851341,
			"mid": "4084802572851341",
			"idstr": "4084802572851341",
			"text": "2",
'''


# http://m.weibo.cn/mblogDeal/delMyMblog
#  删除自己的单条帖子
def weibo_delete_single_post(login_data, id):
    if id:
        req = common_request_maker('http://m.weibo.cn/mblogDeal/delMyMblog')
        req.add_header('Origin', 'http://m.weibo.cn')
        req.add_header('Referer', 'http://m.weibo.cn/?jumpfrom=weibocom')
        req.add_header('Cookie', login_data['cookie'])
        data = urllib.parse.urlencode({'id': id})
        data = bytes(data, 'utf-8')

        try:
            response = urllib.request.urlopen(req, data, timeout=10)
        except urllib.error.HTTPError as e:
            log(e)
            return
        res_str = str(response.read(), 'utf-8')
        log('删除自己的单条帖子 返回内容-----------')
        log(res_str)
        log('删除自己的单条帖子 返回内容-----------')


# http://m.weibo.cn/mblogDeal/addAMblog
# 微博直接发普通帖子
def weibo_send_single_post(login_data, content):
    if content:
        req = common_request_maker('http://m.weibo.cn/mblogDeal/addAMblog')
        req.add_header('Origin', 'http://m.weibo.cn')
        req.add_header('Referer', 'http://m.weibo.cn/mblog')
        req.add_header('Cookie', login_data['cookie'])
        data = urllib.parse.urlencode({'content': content})
        data = bytes(data, 'utf-8')

        try:
            response = urllib.request.urlopen(req, data, timeout=10)
        except urllib.error.HTTPError as e:
            log(e)
            return
        res_str = str(response.read(), 'utf-8')
        log('发帖返回内容-----------')
        log(res_str)
        log('发帖返回内容-----------')


# http://m.weibo.cn/mblogDeal/rtMblog
# 转发内容
def weibo_repost(login_data, id, content, rtcomment=None, code=None):
    if id and content:
        req = common_request_maker('http://m.weibo.cn/mblogDeal/rtMblog')
        req.add_header('Origin', 'http://m.weibo.cn')
        req.add_header('Referer', 'http://m.weibo.cn/repost?id=' + id)
        req.add_header('Cookie', login_data['cookie'])
        data = {'content': content, 'id': id}
        if rtcomment:
            data['rtcomment'] = rtcomment
        if code:
            data['code'] = code
        data = bytes(urllib.parse.urlencode(data), 'utf-8')
        # req.add_header('Content-Length', len(data))

        try:
            response = urllib.request.urlopen(req, data, timeout=10)
        except urllib.error.HTTPError as e:
            log(e)
            return
        res_str = str(response.read(), 'utf-8')
        log('转发内容 返回内容-----------')
        log(res_str)
        log('转发内容 返回内容-----------')

        try:
            res_obj = json.loads(res_str)
            if str(res_obj['ok']) == '-3':
                return str(res_obj['captId'])

        except BaseException as e:
            log(e)


# http://m.weibo.cn/api/comments/create
# 评论微博,这个接口比较麻烦,st这东西得从其他接口去拿,而且有时候每个帖子还不一样,所以以后需要再弄
def weibo_comment(login_data, id, st, content, repost=None):
    if id and content:
        req = common_request_maker('http://m.weibo.cn/api/comments/create')
        req.add_header('Origin', 'http://m.weibo.cn')
        req.add_header('Referer', 'http://m.weibo.cn/compose/comment?id=' + id)

        # req.add_header('X-Requested-With', 'XMLHttpRequest')
        # req.add_header('Accept', 'application/json, text/plain, */*')
        # req.add_header('Accept-Charset', 'utf-8, iso-8859-1, utf-16, *;q=0.7')
        # req.add_header('Accept-Encoding', 'gzip,deflate')
        # req.add_header('Accept-Language', 'en-US')


        req.add_header('Cookie', login_data['cookie'])
        if repost:
            data = urllib.parse.urlencode({'content': content, 'id': id, 'mid': id, 'st': st, 'dualPost': '1'})
        else:
            data = urllib.parse.urlencode({'content': content, 'id': id, 'mid': id, 'st': st})
        data = bytes(data, 'utf-8')

        try:
            response = urllib.request.urlopen(req, data, timeout=10)
        except urllib.error.HTTPError as e:
            log(e)
            return
        res_str = str(response.read(), 'utf-8')
        log('评论微博 返回内容-----------')
        log(res_str)
        log('评论微博 返回内容-----------')


# http://m.weibo.cn/api/friendships/destory
# uid=
# 删除好友

# http://m.weibo.cn/api/friendships/create
# uid=
# 添加好友


# 获取某条微博的评论
# http://m.weibo.cn/api/comments/show?id=4084847486563541&page=1







class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.create_ui()

    def create_ui(self):
        self.account_label = Label(self, text='Account账号:')
        self.account_label.pack()
        self.account_input = Entry(self)
        self.account_input.pack()

        self.passwd_label = Label(self, text='Password密码:')
        self.passwd_label.pack()
        self.passwd_input = Entry(self)
        self.passwd_input.pack()

        self.init_button = Button(self, text='Init初始化', command=self.init)
        self.init_button.pack()

        self.log_label = Label(self, text='Log日志:')
        self.log_label.config()
        self.log_label.pack()

        self.info_frame = Frame(self)
        self.info_frame.pack()

        self.info_text = Text(self.info_frame, height=10, width=100, bd=5, bg='#9c9c9c')
        self.info_text.pack(side=LEFT, fill=Y)
        # self.info_text.configure()
        self.info_text.scroll = Scrollbar(self.info_frame)
        self.info_text.scroll.pack(side=RIGHT, fill=Y)
        self.info_text.scroll.config(command=self.info_text.yview)
        self.info_text.config(yscrollcommand=self.info_text.scroll.set)

        self.func_frame = Frame(self)
        self.func_frame.pack()
        self.func_del_button = Button(self.func_frame, text='Del_post删除帖子', command=self.func_del)
        self.func_del_button.pack(side=LEFT)
        self.func_ban_button = Button(self.func_frame, text='ban_account封号', command=self.func_ban)
        self.func_ban_button.pack(side=RIGHT)

        self.ban_frame = Frame(self, height=400, width=300, bd=5, bg='#9c9c9c')
        self.ban_frame.pack()

    def init(self):
        login_data = weibo_login(self.account_input.get(), self.passwd_input.get())
        if login_data:
            self.login_data = login_data
            self.init_button.configure(state='disabled')

    def func_del(self):
        if self.login_data:
            self.func_del_button.configure(state='disabled')
            threading.Thread(target=self.weibo_del_all_my_post(self.login_data)).start()

    # 删除自己的所有微博,->获取列表拿第一项->删除->延时10秒->再获取列表如此反复
    def weibo_del_all_my_post(self, login_data):
        for i in range(999999):
            id = weibo_get_my_posts(login_data)
            if id:
                weibo_delete_single_post(login_data, id)
                time.sleep(10)
                log('等待10秒')
            else:
                break

    def func_ban(self):
        if self.login_data:
            self.func_ban_button.configure(state='disabled')
            threading.Thread(target=self.try_ban(
                self.login_data, '1000粉仅售0.5元,专业服务值得信赖,需要的请快速联系!!', 500, 30)).start()

    # 发垃圾贴->获取列表遍历所有帖子->发垃圾->延时10秒->再获取列表如此反复
    def try_ban(self, login_data, content, times, duration):
        for i in range(times - 1):
            posts = weibo_homepage(login_data)
            for post in posts:
                captId = weibo_repost(login_data, post['mblog']['id'], content, post['mblog']['user']['id'])
                if captId:
                    self.add_block(login_data, post['mblog']['id'], content, post['mblog']['user']['id'], captId)
                time.sleep(duration)

    def add_block(self, login_data, content, times, duration, captId):
        # 这里是因为发帖太多需要验证码所致,本来设计是GUI用户自己识别,输入,在weibo_repost添加code参数实现
        # GUI的设计是取得验证码图片后,在Frame里面加一个block,有文本框,确认按钮,将验证码输入文本框然后点确定,然后
        # 这个block从fame中移除,同时在发起网络请求重试,但是我准备实现这部分代码的时候。。。微博账号被封了。。。2333333
        # 所以就没有必要再搞了。。。以后用到再说吧
        pass

    def app_pirnt(self, str):
        self.info_text.insert(END, str + "\n")


app = None


def log(str):
    print(str)
    if app:
        app.app_pirnt(str)


if __name__ == "__main__":

    app = Application()
    # 设置窗口标题:
    app.master.title('喵喵喵')
    # 主消息循环:
    app.mainloop()

    # if obj:
        # weibo_del_all_my_post()
        # weibo_send_single_post('6553555')
        # weibo_comment(weibo_homepage(), obj['st'], 'aaaaa')

        # send_span("1000粉仅售0.5元,专业服务值得信赖,需要的请快速联系!!" + str(datetime.datetime.now().timestamp()), 500, 60)

        # pass

    pass
