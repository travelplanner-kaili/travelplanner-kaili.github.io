# Dal Moro's (2026-11-27). Venice list = the numbered menu in her article (monicaineurope.com/venice-dal-moros-freshpastatogo, Chinese as written there);
# second list = the brand's own site menu (dalmoros.cn / .it, which is the Málaga shop), ingredients and prices from that page. [Italian, note, 中文, price]
VENICE = [('1', 'Bolognese', '波隆那義大利肉醬麵'), ('2', 'Romana', '培根蛋黃麵'), ('3', 'Padovana', '奶油蘑菇雞肉義大利麵'),
          ('4', 'Genovese', '蒜香羅勒義大利麵'), ('5', 'Calabrese', '蒜香特級冷壓橄欖油義大利麵'), ('6', 'Pescatora', '蕃茄海鮮義大利麵'),
          ('7', 'Veneziana', '墨魚海鮮義大利麵'), ('8', 'Napoletana', '蒜香番茄義大利麵'), ('9', 'Gorgonzola', '奶油起司義大利麵')]
SITE = [
  ('Bolognese', '牛絞肉、番茄醬、蒜、迷迭香、巴西里、帕瑪森起司、蔬菜底（紅蘿蔔、芹菜、洋蔥）', '波隆那肉醬', '10.00'),
  ('Amatriciana', '煙燻豬頰肉、佩科里諾起司、黑胡椒、番茄醬', '阿瑪翠斯番茄醬', '12.00'),
  ('Gricia', '煙燻豬頰肉、佩科里諾起司、黑胡椒', '格里洽（白醬版的阿瑪翠斯）', '12.50'),
  ('Carbonara', '煙燻豬頰肉、佩科里諾起司、黑胡椒、殺菌蛋黃', '培根蛋黃麵', '13.00'),
  ('Chicken Carbonara', '雞肉條、佩科里諾起司、巴西里、黑胡椒、殺菌蛋黃', '雞肉培根蛋黃麵', '12.00'),
  ('Chicken Amatriciana', '雞肉條、佩科里諾起司、巴西里、黑胡椒、番茄醬', '雞肉阿瑪翠斯', '12.00'),
  ('Veneziana', '蒜、去殼蝦仁、巴西里、番茄醬、墨魚汁', '威尼斯墨魚汁海鮮', '12.00'),
  ('Caprese', '番茄醬、布拉塔起司、新鮮番茄、羅勒、迷迭香、巴薩米克醋、蒜', '卡布里風味（素）', '11.00'),
  ('Pesto', '羅勒醬、松子、腰果、核桃、帕瑪森、佩科里諾起司、蒜', '青醬（素）', '11.00'),
  ('Cacio e Pepe', '佩科里諾起司、黑胡椒', '黑胡椒起司（素）', '11.00'),
  ('Tartufo', '黑松露醬、佩科里諾起司、巴西里', '黑松露醬（素）', '12.00'),
  ('Pomodoro', '番茄醬、蒜、羅勒、奧勒岡、巴西里、迷迭香', '番茄蒜香（全素）', '8.00'),
  ('Arrabbiata', '番茄醬、辣椒、蒜、羅勒、奧勒岡、巴西里、迷迭香', '香辣番茄（全素）', '8.50'),
  ('Aglio, olio e peperoncino', '特級初榨橄欖油、蒜、辣椒、開心果碎', '蒜香辣油（全素）', '7.00'),
]
MENU = [['威尼斯店（推薦文，點餐說號碼）', [[f'{n}. {it}', '', zh, ''] for n, it, zh in VENICE]],
        ['品牌官網菜單（馬拉加分店，參考用料）', [[it, ing, zh, p] for it, ing, zh, p in SITE]]]
MENU_NOTE = ['點餐跟店員說號碼就好，每種醬會配合適的麵；加麵或加料（橄欖、起司、蒜頭、蘑菇、辣椒）另加 €0.5–1（推薦文資料）。',
             '店員最推 7 號墨魚麵。',
             '第二份是品牌官網上的菜單，那是西班牙馬拉加分店的；威尼斯店的口味和價格不一定一樣，用來看用料和過敏原參考。']
