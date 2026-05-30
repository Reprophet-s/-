from typing import Any


LOCAL_CITY_DATA: dict[str, dict[str, Any]] = {
    "北京": {
        "aliases": ["北京市"],
        "profile": "历史文化、皇家园林、博物馆和城市地标密集，适合按中轴线、海淀文化区、朝阳夜生活分区游玩。",
        "weather_tips": ["春秋适合步行和胡同游；夏季注意防晒补水；冬季户外风大，故宫、国博等室内点更稳。"],
        "pois": [
            {"name": "故宫博物院", "type": "博物馆/历史文化", "area": "天安门-王府井", "tags": ["博物馆", "历史文化", "亲子"], "indoor": True, "cost": 60, "duration": 180, "reason": "北京最核心的历史文化体验，适合安排在上午。"},
            {"name": "天安门广场", "type": "城市地标", "area": "天安门-王府井", "tags": ["历史文化", "自然风光"], "indoor": False, "cost": 0, "duration": 60, "reason": "和故宫、中轴线可以自然串联。"},
            {"name": "国家博物馆", "type": "博物馆", "area": "天安门-王府井", "tags": ["博物馆", "历史文化", "亲子"], "indoor": True, "cost": 0, "duration": 150, "reason": "雨天和高温天都很友好，内容扎实。"},
            {"name": "颐和园", "type": "皇家园林", "area": "海淀", "tags": ["自然风光", "历史文化", "亲子"], "indoor": False, "cost": 30, "duration": 180, "reason": "湖景和园林结合，适合半日慢游。"},
            {"name": "圆明园", "type": "遗址公园", "area": "海淀", "tags": ["历史文化", "自然风光"], "indoor": False, "cost": 25, "duration": 120, "reason": "可与颐和园或清华北大周边组合。"},
            {"name": "什刹海", "type": "胡同/湖区", "area": "后海-鼓楼", "tags": ["夜景", "咖啡", "历史文化"], "indoor": False, "cost": 0, "duration": 120, "reason": "傍晚散步和夜景氛围好。"},
            {"name": "南锣鼓巷", "type": "特色街区", "area": "后海-鼓楼", "tags": ["美食", "购物", "咖啡"], "indoor": False, "cost": 80, "duration": 90, "reason": "适合穿插小吃和文创店，但节假日较拥挤。"},
            {"name": "三里屯太古里", "type": "商圈", "area": "朝阳", "tags": ["购物", "夜景", "美食", "咖啡"], "indoor": True, "cost": 120, "duration": 120, "reason": "夜间餐饮和购物选择丰富。"},
        ],
        "foods": ["北京烤鸭", "涮羊肉", "炸酱面", "豆汁焦圈", "卤煮火烧"],
        "rainy_backups": ["国家博物馆", "首都博物馆", "三里屯太古里", "侨福芳草地"],
    },
    "广州": {
        "aliases": ["广州市"],
        "profile": "岭南文化、美食早茶、珠江夜景和城市商圈突出，节奏适合早茶开场、午后室内、夜游收尾。",
        "weather_tips": ["夏季湿热且阵雨多，午后建议安排商场、博物馆或茶楼；夜晚适合珠江沿线。"],
        "pois": [
            {"name": "陈家祠", "type": "历史文化", "area": "荔湾", "tags": ["历史文化", "博物馆"], "indoor": True, "cost": 10, "duration": 90, "reason": "岭南建筑和工艺代表，适合文化路线开场。"},
            {"name": "沙面岛", "type": "历史街区", "area": "荔湾", "tags": ["历史文化", "咖啡", "自然风光"], "indoor": False, "cost": 0, "duration": 120, "reason": "街区尺度舒服，适合拍照和咖啡休息。"},
            {"name": "永庆坊", "type": "特色街区", "area": "荔湾", "tags": ["美食", "历史文化", "购物"], "indoor": False, "cost": 60, "duration": 120, "reason": "老城更新街区，适合和荔湾湖、上下九组合。"},
            {"name": "广东省博物馆", "type": "博物馆", "area": "珠江新城", "tags": ["博物馆", "亲子", "历史文化"], "indoor": True, "cost": 0, "duration": 120, "reason": "雨天和高温天首选，旁边就是花城广场。"},
            {"name": "广州塔", "type": "城市地标", "area": "海珠", "tags": ["夜景", "亲子"], "indoor": True, "cost": 150, "duration": 120, "reason": "广州代表性夜景点，适合傍晚到夜间。"},
            {"name": "珠江夜游", "type": "夜游", "area": "珠江沿线", "tags": ["夜景", "亲子"], "indoor": False, "cost": 120, "duration": 90, "reason": "能集中看到珠江两岸夜景。"},
            {"name": "北京路步行街", "type": "商圈", "area": "越秀", "tags": ["购物", "美食", "历史文化"], "indoor": False, "cost": 80, "duration": 120, "reason": "吃逛集中，交通便利。"},
        ],
        "foods": ["广式早茶", "肠粉", "云吞面", "烧鹅", "双皮奶"],
        "rainy_backups": ["广东省博物馆", "正佳广场", "天河城", "K11"],
    },
    "西双版纳": {
        "aliases": ["景洪", "西双版纳傣族自治州"],
        "profile": "热带雨林、傣族风情、夜市和亲近自然体验突出，行程要避开正午高温。",
        "weather_tips": ["雨林地区阵雨常见，带防蚊用品和轻便雨具；户外活动尽量安排上午。"],
        "pois": [
            {"name": "中国科学院西双版纳热带植物园", "type": "自然风光", "area": "勐腊", "tags": ["自然风光", "亲子", "徒步"], "indoor": False, "cost": 80, "duration": 240, "reason": "版纳最硬核的自然体验，适合安排完整半天。"},
            {"name": "曼听公园", "type": "城市公园", "area": "景洪", "tags": ["自然风光", "历史文化", "亲子"], "indoor": False, "cost": 40, "duration": 150, "reason": "离市区近，傣式建筑和园林体验集中。"},
            {"name": "总佛寺", "type": "历史文化", "area": "景洪", "tags": ["历史文化"], "indoor": False, "cost": 0, "duration": 60, "reason": "可与曼听公园顺路组合。"},
            {"name": "告庄西双景", "type": "特色街区", "area": "景洪", "tags": ["夜景", "美食", "购物"], "indoor": False, "cost": 100, "duration": 180, "reason": "夜市、餐饮和拍照集中，适合晚间。"},
            {"name": "星光夜市", "type": "夜市", "area": "告庄", "tags": ["夜景", "美食", "购物"], "indoor": False, "cost": 120, "duration": 150, "reason": "版纳夜间体验代表，但人流较大。"},
            {"name": "野象谷", "type": "自然景区", "area": "景洪北部", "tags": ["自然风光", "亲子"], "indoor": False, "cost": 60, "duration": 180, "reason": "亲子自然路线常选，适合上午出发。"},
            {"name": "傣族园", "type": "民族文化", "area": "橄榄坝", "tags": ["历史文化", "亲子"], "indoor": False, "cost": 45, "duration": 180, "reason": "了解傣族村寨和泼水文化。"},
        ],
        "foods": ["傣味手抓饭", "香茅草烤鱼", "菠萝饭", "舂鸡脚", "老挝冰咖啡"],
        "rainy_backups": ["告庄西双景室内餐饮", "民族工艺体验店", "酒店休整+夜市"],
    },
    "上海": {
        "aliases": ["上海市"],
        "profile": "城市地标、博物馆、海派街区、购物和夜景突出，适合地铁串联。",
        "weather_tips": ["梅雨季雨具必备；夏季午后适合博物馆和商场；夜景建议避开大雾和强降雨。"],
        "pois": [
            {"name": "外滩", "type": "城市地标", "area": "黄浦", "tags": ["夜景", "历史文化"], "indoor": False, "cost": 0, "duration": 90, "reason": "上海第一眼城市名片，傍晚到夜间最佳。"},
            {"name": "南京东路步行街", "type": "商圈", "area": "黄浦", "tags": ["购物", "美食", "夜景"], "indoor": False, "cost": 80, "duration": 90, "reason": "可与外滩自然串联。"},
            {"name": "上海博物馆", "type": "博物馆", "area": "人民广场", "tags": ["博物馆", "历史文化", "亲子"], "indoor": True, "cost": 0, "duration": 150, "reason": "雨天或炎热天气很稳。"},
            {"name": "武康路", "type": "海派街区", "area": "徐汇", "tags": ["咖啡", "历史文化", "购物"], "indoor": False, "cost": 80, "duration": 120, "reason": "适合慢走、咖啡和建筑观察。"},
            {"name": "豫园", "type": "园林/历史街区", "area": "黄浦", "tags": ["历史文化", "美食", "购物"], "indoor": False, "cost": 40, "duration": 120, "reason": "园林和老城厢小吃集中。"},
            {"name": "陆家嘴", "type": "城市地标", "area": "浦东", "tags": ["夜景", "购物"], "indoor": True, "cost": 120, "duration": 120, "reason": "高楼观景、商场和夜景集中。"},
            {"name": "上海迪士尼度假区", "type": "主题乐园", "area": "浦东", "tags": ["亲子"], "indoor": False, "cost": 475, "duration": 480, "reason": "亲子和主题乐园需求优先级高，但需要单独留一天。"},
        ],
        "foods": ["生煎", "小笼包", "本帮菜", "葱油拌面", "鲜肉月饼"],
        "rainy_backups": ["上海博物馆", "上海自然博物馆", "前滩太古里", "陆家嘴商圈"],
    },
    "长沙": {
        "aliases": ["长沙市"],
        "profile": "美食、夜生活、湖湘文化和年轻消费街区突出，适合夜间体验，但要控制排队时间。",
        "weather_tips": ["夏季炎热，白天适合室内博物馆；夜间逛街和夜宵更舒服。"],
        "pois": [
            {"name": "湖南博物院", "type": "博物馆", "area": "开福", "tags": ["博物馆", "历史文化", "亲子"], "indoor": True, "cost": 0, "duration": 180, "reason": "长沙文化路线核心，适合上午或雨天。"},
            {"name": "岳麓山", "type": "自然风光", "area": "岳麓", "tags": ["自然风光", "历史文化", "徒步"], "indoor": False, "cost": 0, "duration": 180, "reason": "自然和书院文化结合，建议上午避热。"},
            {"name": "岳麓书院", "type": "历史文化", "area": "岳麓", "tags": ["历史文化", "博物馆"], "indoor": True, "cost": 40, "duration": 90, "reason": "可与岳麓山、湖南大学串联。"},
            {"name": "橘子洲", "type": "城市地标", "area": "湘江", "tags": ["自然风光", "夜景"], "indoor": False, "cost": 0, "duration": 120, "reason": "湘江景观代表，傍晚更舒服。"},
            {"name": "五一广场", "type": "商圈", "area": "五一商圈", "tags": ["美食", "购物", "夜景"], "indoor": True, "cost": 100, "duration": 150, "reason": "吃逛高度集中，适合作为夜间主场。"},
            {"name": "太平老街", "type": "特色街区", "area": "五一商圈", "tags": ["美食", "购物", "历史文化"], "indoor": False, "cost": 80, "duration": 120, "reason": "小吃和街区氛围强，但高峰期拥挤。"},
            {"name": "谢子龙影像艺术馆", "type": "艺术馆", "area": "洋湖", "tags": ["博物馆", "咖啡"], "indoor": True, "cost": 80, "duration": 120, "reason": "适合拍照、展览和午后避暑。"},
        ],
        "foods": ["臭豆腐", "糖油粑粑", "小龙虾", "剁椒鱼头", "茶颜悦色"],
        "rainy_backups": ["湖南博物院", "谢子龙影像艺术馆", "IFS国金中心", "万家丽广场"],
    },
    "武汉": {
        "aliases": ["武汉市"],
        "profile": "江城风光、大学人文、博物馆和过早美食鲜明，三镇之间要注意路线分区。",
        "weather_tips": ["夏季炎热，黄鹤楼和东湖建议早晚；雨天可转湖北省博物馆和商圈。"],
        "pois": [
            {"name": "黄鹤楼", "type": "历史地标", "area": "武昌", "tags": ["历史文化", "自然风光"], "indoor": False, "cost": 70, "duration": 120, "reason": "武汉经典地标，适合与长江大桥、户部巷组合。"},
            {"name": "湖北省博物馆", "type": "博物馆", "area": "东湖", "tags": ["博物馆", "历史文化", "亲子"], "indoor": True, "cost": 0, "duration": 150, "reason": "雨天首选，馆藏辨识度高。"},
            {"name": "东湖听涛/磨山", "type": "自然风光", "area": "东湖", "tags": ["自然风光", "亲子", "徒步"], "indoor": False, "cost": 0, "duration": 180, "reason": "湖区景观开阔，适合骑行和慢游。"},
            {"name": "武汉大学", "type": "校园/历史建筑", "area": "武昌", "tags": ["历史文化", "自然风光"], "indoor": False, "cost": 0, "duration": 90, "reason": "校园建筑和人文氛围适合轻量安排。"},
            {"name": "江汉路步行街", "type": "商圈", "area": "汉口", "tags": ["美食", "购物", "夜景"], "indoor": False, "cost": 80, "duration": 120, "reason": "汉口吃逛中心，可接江滩夜景。"},
            {"name": "汉口江滩", "type": "江景", "area": "汉口", "tags": ["夜景", "自然风光"], "indoor": False, "cost": 0, "duration": 90, "reason": "傍晚散步和夜景都不错。"},
            {"name": "户部巷", "type": "美食街", "area": "武昌", "tags": ["美食"], "indoor": False, "cost": 60, "duration": 75, "reason": "适合尝试小吃，但可作为顺路点而非唯一美食目的地。"},
        ],
        "foods": ["热干面", "三鲜豆皮", "面窝", "藕汤", "武昌鱼"],
        "rainy_backups": ["湖北省博物馆", "武汉天地", "楚河汉街", "万象城"],
    },
    "杭州": {
        "aliases": ["杭州市"],
        "profile": "西湖山水、寺院茶文化、博物馆和江南街区突出，适合按西湖、灵隐、运河分区。",
        "weather_tips": ["雨天的西湖也有氛围，但长时间户外需备伞；夏季午后可安排博物馆和茶馆。"],
        "pois": [
            {"name": "西湖断桥-白堤", "type": "自然风光", "area": "西湖", "tags": ["自然风光", "历史文化"], "indoor": False, "cost": 0, "duration": 120, "reason": "杭州第一站经典路线，适合上午慢走。"},
            {"name": "苏堤", "type": "自然风光", "area": "西湖", "tags": ["自然风光", "徒步"], "indoor": False, "cost": 0, "duration": 120, "reason": "西湖深度步行体验，天气好时优先。"},
            {"name": "灵隐寺", "type": "寺院", "area": "灵隐", "tags": ["历史文化", "自然风光"], "indoor": False, "cost": 75, "duration": 150, "reason": "杭州寺院和山林体验代表。"},
            {"name": "法喜寺", "type": "寺院", "area": "西湖西南", "tags": ["历史文化", "自然风光"], "indoor": False, "cost": 10, "duration": 90, "reason": "氛围轻松，适合和茶园路线组合。"},
            {"name": "中国茶叶博物馆", "type": "博物馆", "area": "龙井", "tags": ["博物馆", "咖啡", "历史文化"], "indoor": True, "cost": 0, "duration": 120, "reason": "雨天和午后都适合，能接龙井茶文化。"},
            {"name": "河坊街", "type": "特色街区", "area": "上城", "tags": ["美食", "购物", "历史文化"], "indoor": False, "cost": 80, "duration": 120, "reason": "晚餐和伴手礼方便，但高峰期人多。"},
            {"name": "京杭大运河杭州段", "type": "城市水岸", "area": "拱墅", "tags": ["夜景", "历史文化", "咖啡"], "indoor": False, "cost": 60, "duration": 120, "reason": "比西湖更安静，适合傍晚水岸散步。"},
        ],
        "foods": ["西湖醋鱼", "东坡肉", "龙井虾仁", "片儿川", "葱包桧"],
        "rainy_backups": ["中国茶叶博物馆", "浙江省博物馆", "杭州大厦", "湖滨银泰in77"],
    },
    "苏州": {
        "aliases": ["苏州市"],
        "profile": "古典园林、古城水巷、评弹和江南美食突出，适合慢节奏步行。",
        "weather_tips": ["雨天园林也有江南氛围，但石板路易滑；高温天可减少户外园林数量。"],
        "pois": [
            {"name": "拙政园", "type": "古典园林", "area": "姑苏", "tags": ["历史文化", "自然风光"], "indoor": False, "cost": 80, "duration": 150, "reason": "苏州园林代表，适合上午避开人流。"},
            {"name": "苏州博物馆", "type": "博物馆", "area": "姑苏", "tags": ["博物馆", "历史文化", "亲子"], "indoor": True, "cost": 0, "duration": 120, "reason": "建筑和展览都值得看，雨天很稳。"},
            {"name": "狮子林", "type": "古典园林", "area": "姑苏", "tags": ["历史文化", "亲子"], "indoor": False, "cost": 40, "duration": 90, "reason": "假山迷宫适合亲子，也能与苏博/拙政园串联。"},
            {"name": "平江路", "type": "历史街区", "area": "姑苏", "tags": ["美食", "咖啡", "历史文化", "购物"], "indoor": False, "cost": 80, "duration": 150, "reason": "水巷、咖啡和小吃集中，适合下午到傍晚。"},
            {"name": "山塘街", "type": "夜景街区", "area": "姑苏", "tags": ["夜景", "美食", "购物"], "indoor": False, "cost": 80, "duration": 120, "reason": "夜景氛围强，适合晚间收尾。"},
            {"name": "诚品生活苏州", "type": "商圈/书店", "area": "金鸡湖", "tags": ["购物", "咖啡"], "indoor": True, "cost": 80, "duration": 120, "reason": "雨天或想换现代城市体验时合适。"},
            {"name": "金鸡湖", "type": "城市湖景", "area": "园区", "tags": ["夜景", "自然风光"], "indoor": False, "cost": 0, "duration": 120, "reason": "现代苏州夜景，适合和诚品组合。"},
        ],
        "foods": ["松鼠鳜鱼", "苏式面", "生煎", "桂花糖藕", "鸡头米"],
        "rainy_backups": ["苏州博物馆", "诚品生活苏州", "苏州中心", "评弹茶馆"],
    },
    "长春": {
        "aliases": ["长春市"],
        "profile": "汽车工业、电影文化、伪满历史、冰雪体验和东北洗浴文化鲜明，适合把白天文化景点和夜间休闲体验组合起来。",
        "weather_tips": ["冬季寒冷且风大，户外活动注意保暖；夜间很适合安排洗浴、汗蒸和东北菜。"],
        "pois": [
            {"name": "伪满皇宫博物院", "type": "博物馆/历史文化", "area": "宽城", "tags": ["博物馆", "历史文化"], "indoor": True, "cost": 70, "duration": 150, "reason": "长春最有辨识度的历史文化景点，适合上午安排。"},
            {"name": "长影旧址博物馆", "type": "电影文化", "area": "朝阳", "tags": ["博物馆", "历史文化", "亲子"], "indoor": True, "cost": 90, "duration": 120, "reason": "能体现长春电影城气质，雨雪天也友好。"},
            {"name": "净月潭国家森林公园", "type": "自然风光", "area": "净月", "tags": ["自然风光", "徒步", "亲子"], "indoor": False, "cost": 30, "duration": 180, "reason": "城市近郊自然体验代表，天气好时优先。"},
            {"name": "这有山", "type": "特色商圈", "area": "红旗街", "tags": ["美食", "购物", "夜景", "咖啡"], "indoor": True, "cost": 100, "duration": 120, "reason": "室内街区形态特别，适合下午或夜间吃逛。"},
            {"name": "桂林路", "type": "美食街区", "area": "朝阳", "tags": ["美食", "夜景"], "indoor": False, "cost": 80, "duration": 120, "reason": "长春年轻人常去的吃逛区域，适合晚餐和夜宵。"},
            {"name": "南湖公园", "type": "城市公园", "area": "朝阳", "tags": ["自然风光", "亲子"], "indoor": False, "cost": 0, "duration": 90, "reason": "市区内轻松散步点，可作为低强度安排。"},
            {"name": "长春世界雕塑园", "type": "艺术公园", "area": "南关", "tags": ["自然风光", "博物馆", "亲子"], "indoor": False, "cost": 60, "duration": 150, "reason": "公园和艺术结合，适合天气好的半日游。"},
        ],
        "foods": ["锅包肉", "东北铁锅炖", "烧烤", "冷面", "粘豆包"],
        "rainy_backups": ["伪满皇宫博物院", "长影旧址博物馆", "这有山", "洗浴汗蒸"],
    },
}


LOCAL_ACTIVITIES: dict[str, list[dict[str, Any]]] = {
    "长春": [
        {"name": "东北洗浴汗蒸", "type": "本地休闲", "area": "红旗街/桂林路/净月", "tags": ["洗浴", "汗蒸", "休闲", "夜间"], "indoor": True, "cost": 120, "duration": 150, "keyword": "洗浴汗蒸", "reason": "长春很适合把夜间留给东北洗浴和汗蒸，能缓解一天步行疲劳，也有本地生活感。"},
        {"name": "东北烧烤夜宵", "type": "本地美食活动", "area": "桂林路/红旗街", "tags": ["美食", "夜间", "烧烤"], "indoor": True, "cost": 100, "duration": 120, "keyword": "烧烤", "reason": "夜间安排烧烤或夜宵更贴近东北城市节奏。"},
        {"name": "电影文化体验", "type": "文化体验", "area": "长影旧址周边", "tags": ["电影", "历史文化"], "indoor": True, "cost": 90, "duration": 120, "keyword": "电影", "reason": "长春有电影城背景，电影相关展馆和街区适合文化体验。"},
        {"name": "冰雪体验", "type": "季节活动", "area": "净月/莲花山", "tags": ["冰雪", "亲子", "冬季"], "indoor": False, "cost": 180, "duration": 180, "keyword": "滑雪", "reason": "冬季可把滑雪、冰雪乐园作为长春特色活动。"},
    ],
    "北京": [
        {"name": "胡同咖啡/茶馆", "type": "本地休闲", "area": "后海-鼓楼", "tags": ["咖啡", "茶馆", "历史文化"], "indoor": True, "cost": 80, "duration": 90, "keyword": "胡同 咖啡", "reason": "在胡同里安排一段咖啡或茶馆休息，比纯打卡更舒服。"},
    ],
    "广州": [
        {"name": "广式早茶体验", "type": "本地美食活动", "area": "荔湾/越秀/天河", "tags": ["美食", "早茶"], "indoor": True, "cost": 100, "duration": 90, "keyword": "早茶", "reason": "广州行程适合用早茶开场，既是用餐也是本地文化体验。"},
    ],
    "长沙": [
        {"name": "夜宵小龙虾", "type": "本地美食活动", "area": "五一商圈/湘江中路", "tags": ["美食", "夜间", "小龙虾"], "indoor": True, "cost": 120, "duration": 120, "keyword": "小龙虾", "reason": "长沙夜生活很强，夜宵比普通晚餐更有城市特色。"},
    ],
}

LOCAL_RESTAURANTS: dict[str, list[dict[str, Any]]] = {
    "北京": [
        {"name": "四季民福烤鸭店", "type": "北京菜/烤鸭", "area": "东城", "address": "故宫、王府井周边多店", "cost": 160, "signature": "北京烤鸭"},
        {"name": "全聚德", "type": "北京菜/烤鸭", "area": "前门", "address": "前门大街周边", "cost": 180, "signature": "北京烤鸭"},
        {"name": "东来顺", "type": "涮羊肉", "area": "东城", "address": "王府井、前门等商圈多店", "cost": 140, "signature": "涮羊肉"},
        {"name": "护国寺小吃", "type": "北京小吃", "area": "西城", "address": "护国寺街周边", "cost": 40, "signature": "炸酱面/豆汁焦圈"},
        {"name": "姚记炒肝", "type": "北京小吃", "area": "鼓楼", "address": "鼓楼湾周边", "cost": 35, "signature": "炒肝/包子"},
    ],
    "广州": [
        {"name": "点都德", "type": "广式早茶", "area": "越秀/天河/荔湾", "address": "广州多店", "cost": 90, "signature": "广式早茶"},
        {"name": "陶陶居", "type": "粤菜/早茶", "area": "荔湾", "address": "第十甫路周边", "cost": 110, "signature": "虾饺/烧鹅"},
        {"name": "广州酒家", "type": "粤菜", "area": "荔湾/越秀", "address": "广州多店", "cost": 120, "signature": "文昌鸡/早茶"},
        {"name": "南信牛奶甜品专家", "type": "甜品", "area": "荔湾", "address": "第十甫路周边", "cost": 30, "signature": "双皮奶"},
        {"name": "炳胜品味", "type": "粤菜", "area": "天河/海珠", "address": "广州多店", "cost": 150, "signature": "烧鹅/啫啫煲"},
    ],
    "西双版纳": [
        {"name": "曼飞龙烤鸡", "type": "傣味", "area": "景洪", "address": "告庄西双景周边", "cost": 90, "signature": "香茅草烤鸡"},
        {"name": "啰啰冰屋", "type": "甜品/简餐", "area": "景洪", "address": "景洪城区", "cost": 45, "signature": "泡鲁达/舂鸡脚"},
        {"name": "婉泰老挝冰咖啡", "type": "咖啡/东南亚甜品", "area": "告庄", "address": "告庄西双景周边", "cost": 40, "signature": "老挝冰咖啡"},
        {"name": "春武里", "type": "东南亚菜", "area": "景洪", "address": "景洪城区", "cost": 100, "signature": "泰式/傣味融合菜"},
        {"name": "猫檬东南亚餐厅", "type": "东南亚菜", "area": "告庄", "address": "告庄西双景周边", "cost": 90, "signature": "冬阴功/菠萝饭"},
    ],
    "上海": [
        {"name": "佳家汤包", "type": "小笼/本帮小吃", "area": "黄浦", "address": "人民广场周边", "cost": 45, "signature": "小笼包"},
        {"name": "小杨生煎", "type": "生煎", "area": "黄浦/静安", "address": "上海多店", "cost": 35, "signature": "生煎"},
        {"name": "老吉士酒家", "type": "本帮菜", "area": "徐汇", "address": "天平路周边", "cost": 220, "signature": "红烧肉/本帮菜"},
        {"name": "南翔馒头店", "type": "小笼", "area": "豫园", "address": "豫园商城周边", "cost": 70, "signature": "南翔小笼"},
        {"name": "莱莱小笼", "type": "小笼", "area": "黄浦", "address": "天津路周边", "cost": 50, "signature": "蟹粉小笼"},
    ],
    "长沙": [
        {"name": "炊烟小炒黄牛肉", "type": "湘菜", "area": "五一商圈", "address": "长沙多店", "cost": 90, "signature": "小炒黄牛肉"},
        {"name": "费大厨辣椒炒肉", "type": "湘菜", "area": "五一商圈", "address": "长沙多店", "cost": 90, "signature": "辣椒炒肉"},
        {"name": "文和友", "type": "长沙小吃/夜宵", "area": "海信广场", "address": "湘江中路周边", "cost": 100, "signature": "小龙虾/长沙小吃"},
        {"name": "黑色经典臭豆腐", "type": "小吃", "area": "五一商圈", "address": "长沙多店", "cost": 20, "signature": "臭豆腐"},
        {"name": "笨罗卜浏阳菜馆", "type": "湘菜", "area": "长沙城区", "address": "长沙多店", "cost": 75, "signature": "浏阳菜"},
    ],
    "武汉": [
        {"name": "蔡林记", "type": "武汉小吃", "area": "江汉/武昌", "address": "武汉多店", "cost": 25, "signature": "热干面"},
        {"name": "老通城", "type": "武汉小吃", "area": "汉口", "address": "汉口城区", "cost": 35, "signature": "三鲜豆皮"},
        {"name": "赵师傅油饼包烧麦", "type": "过早小吃", "area": "武昌", "address": "粮道街周边", "cost": 25, "signature": "油饼包烧麦"},
        {"name": "靓靓蒸虾", "type": "湖北菜/小龙虾", "area": "汉口", "address": "武汉多店", "cost": 130, "signature": "蒸虾"},
        {"name": "湖锦酒楼", "type": "湖北菜", "area": "武昌/汉口", "address": "武汉多店", "cost": 120, "signature": "藕汤/武昌鱼"},
    ],
    "杭州": [
        {"name": "楼外楼", "type": "杭帮菜", "area": "西湖", "address": "孤山路周边", "cost": 150, "signature": "西湖醋鱼/东坡肉"},
        {"name": "知味观", "type": "杭帮小吃", "area": "上城", "address": "仁和路、湖滨周边", "cost": 80, "signature": "小笼/片儿川"},
        {"name": "新白鹿餐厅", "type": "杭帮菜", "area": "湖滨/西湖", "address": "杭州多店", "cost": 70, "signature": "蛋黄鸡翅/杭帮菜"},
        {"name": "绿茶餐厅", "type": "杭帮融合菜", "area": "西湖/湖滨", "address": "杭州多店", "cost": 90, "signature": "杭帮融合菜"},
        {"name": "方老大面", "type": "面馆", "area": "上城", "address": "杭州城区", "cost": 35, "signature": "片儿川"},
    ],
    "苏州": [
        {"name": "松鹤楼", "type": "苏帮菜", "area": "姑苏", "address": "观前街周边", "cost": 150, "signature": "松鼠鳜鱼"},
        {"name": "得月楼", "type": "苏帮菜", "area": "姑苏", "address": "观前街周边", "cost": 150, "signature": "苏帮菜"},
        {"name": "同得兴", "type": "苏式面", "area": "姑苏", "address": "十全街周边", "cost": 45, "signature": "苏式面"},
        {"name": "朱新年点心店", "type": "苏州小吃", "area": "姑苏", "address": "古城周边", "cost": 35, "signature": "汤团/点心"},
        {"name": "裕兴记", "type": "苏式面", "area": "姑苏", "address": "苏州多店", "cost": 45, "signature": "三虾面/苏式面"},
    ],
    "长春": [
        {"name": "元盛居", "type": "东北火锅/炭火锅", "area": "朝阳/南关", "address": "长春多店", "cost": 110, "signature": "炭火锅"},
        {"name": "王记酱骨头", "type": "东北菜", "area": "朝阳", "address": "长春城区", "cost": 80, "signature": "酱骨头"},
        {"name": "春发合饭庄", "type": "老字号东北菜", "area": "南关", "address": "大马路周边", "cost": 90, "signature": "锅包肉/雪衣豆沙"},
        {"name": "状元阁烧烤", "type": "东北烧烤", "area": "桂林路", "address": "桂林路周边", "cost": 90, "signature": "烧烤"},
        {"name": "社会主义新农村", "type": "东北菜", "area": "长春城区", "address": "长春多店", "cost": 85, "signature": "铁锅炖/东北菜"},
    ],
}


def list_city_summaries() -> list[dict[str, Any]]:
    return [
        {
            "name": name,
            "aliases": data.get("aliases", []),
            "profile": data.get("profile", ""),
            "foods": data.get("foods", []),
            "poi_count": len(data.get("pois", [])),
        }
        for name, data in LOCAL_CITY_DATA.items()
    ]


def find_city_data(destination: str) -> dict[str, Any] | None:
    normalized = destination.strip()
    for city, data in LOCAL_CITY_DATA.items():
        aliases = data.get("aliases", [])
        if normalized == city or normalized in aliases or city in normalized:
            return {"name": city, **data}
    return None


def public_city_data(destination: str) -> dict[str, Any] | None:
    city = find_city_data(destination)
    if not city:
        return None
    return {
        "name": city["name"],
        "aliases": city.get("aliases", []),
        "profile": city.get("profile", ""),
        "weather_tips": city.get("weather_tips", []),
        "foods": city.get("foods", []),
        "rainy_backups": city.get("rainy_backups", []),
        "pois": city.get("pois", []),
        "restaurants": LOCAL_RESTAURANTS.get(city["name"], []),
        "activities": LOCAL_ACTIVITIES.get(city["name"], []),
    }


def local_pois_for(destination: str, interests: list[str]) -> list[dict[str, Any]]:
    city = find_city_data(destination)
    if not city:
        return []

    selected_tags = set(_string_items(interests))
    pois = city["pois"]
    if not selected_tags:
        ranked = pois
    else:
        ranked = sorted(
            pois,
            key=lambda poi: len(selected_tags.intersection(set(_string_items(poi.get("tags", []))))),
            reverse=True,
        )
    return [
        {
            "name": poi["name"],
            "type": poi["type"],
            "address": poi.get("area", city["name"]),
            "location": "",
            "source": "local_city_data",
            "local": poi,
        }
        for poi in ranked
    ]


def local_restaurants_for(destination: str) -> list[dict[str, Any]]:
    city = find_city_data(destination)
    if not city:
        return []
    restaurants = LOCAL_RESTAURANTS.get(city["name"], [])
    return [
        {
            "name": restaurant["name"],
            "type": restaurant["type"],
            "address": restaurant["address"],
            "adname": restaurant["area"],
            "location": "",
            "rating": None,
            "cost": restaurant["cost"],
            "tag": restaurant["signature"],
            "photo_url": None,
            "source": "local_restaurant_data",
            "category": "restaurant",
            "local_restaurant": restaurant,
        }
        for restaurant in restaurants
    ]


def local_activities_for(destination: str, interests: list[str]) -> list[dict[str, Any]]:
    city = find_city_data(destination)
    if not city:
        return []
    activities = LOCAL_ACTIVITIES.get(city["name"], [])
    selected_tags = set(_string_items(interests))
    if selected_tags:
        activities = sorted(
            activities,
            key=lambda activity: len(selected_tags.intersection(set(_string_items(activity.get("tags", []))))),
            reverse=True,
        )
    return [
        {
            "name": activity["name"],
            "type": activity["type"],
            "address": activity.get("area", city["name"]),
            "location": "",
            "rating": None,
            "cost": activity.get("cost"),
            "tag": ",".join(_string_items(activity.get("tags", []))),
            "source": "local_activity_data",
            "category": "activity",
            "local_activity": activity,
        }
        for activity in activities
    ]


def local_activity_keywords_for(destination: str) -> list[str]:
    city = find_city_data(destination)
    if not city:
        return []
    return [
        str(activity["keyword"])
        for activity in LOCAL_ACTIVITIES.get(city["name"], [])
        if activity.get("keyword")
    ]


def _string_items(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list | tuple | set):
        items: list[str] = []
        for item in value:
            items.extend(_string_items(item))
        return items
    return [str(value)]
