# SelfBanSinaWeiboAccount
新浪微博账号自毁机器人。。。。。。  
  
我只是想删除微博账号而已，然而并没有这种功能。。。。。。  
  
考虑了一下还是伪装做被盗号发卖粉信息然后等渣浪封号这种办法比较稳妥。  
  
接口选择用微博手机wab版，这个抓包和分析起来比较容易也比较容易伪造。  
  
#流程  
  
1.自己处理好关注和粉丝信息，以免误伤  
2.修改名称和简介，头像，比如“微博卖粉”这种，搞得自己像卖粉的一样  
3.删除所有自己发过的微博，这个可以用程序里面weibodelallmypost()这个方法，点赞回复和足迹这个没做，因为我以前用的时候就没用这种东西。。。  
4.随便加多个微博账号，最好找那种人多的，jc蜀黍啥的避开，自己掂量好，这就是卖粉发评论的目标了，比较危险。。。  

5.send_span(content, times, duration)这就是最关键的方法，它会重复times次，获取微博首页列表（20个），然后对每条微博做出content评论，比如"1000粉仅售0.5元,专业服务值得信赖,需要的请快速联系!!"，为了防止重复评论在后面都会加一串时间戳，并转发到自己的微博，每次操作间隔duration秒。。。。。。然后等着被封就行了吧，大概。。。  




#程序使用的微博接口

https://passport.weibo.cn/sso/login  
微博登陆接口，从这里拿cookie，这是后来的网络请求的基础  
  
http://m.weibo.cn/feed/friends?version=v4  
获取微博首页    

http://m.weibo.cn/mblogDeal/rtMblog  
转发内容，用这个接口来发垃圾信息  
  
http://m.weibo.cn/index/my?format=cards  
微博获取首页自己发的帖子(准备拿来删除用的)  

http://m.weibo.cn/mblogDeal/delMyMblog  
删除自己的单条帖子  


#待使用的接口（可能以后会用吧）  
  
http://m.weibo.cn/api/comments/create  
评论微博,这个接口比较麻烦,st这东西得从其他接口去拿,而且有时候每个帖子还不一样,所以以后需要再弄  


http://m.weibo.cn/api/friendships/destory  
uid=  
删除好友  
  
http://m.weibo.cn/api/friendships/create  
uid=  
添加好友  
  
  
获取某条微博的评论  
http://m.weibo.cn/api/comments/show?id=4084847486563541&page=1  


