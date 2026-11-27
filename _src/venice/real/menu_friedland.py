# Fried Land menu from the Google Maps photo she sent (2026-11-27). [Italian, '', 中文, price]
def _r(rows): return [[it, '', zh, p] for it, zh, p in rows]
MENU = [
 ['炸物 Fried', _r([('1. Nuggets di pollo e patate fritte', '雞塊配薯條', '7.50'), ('2. Patatine fritte', '薯條', '4.00'),
   ('3. Fritto di mare', '綜合炸海鮮', '9.00'), ('4. Calamari fritti', '炸魷魚', '11.00'), ('5. Calamari e gamberi fritti', '炸魷魚和蝦', '10.00'),
   ('6. Gamberi fritti', '炸蝦', '9.50'), ('7. Sardine fritte', '炸沙丁魚', '8.50')])],
 ['沙拉 Insalate', _r([('8. Mediterranea', '地中海沙拉（生菜、番茄、橄欖、芝麻葉、鮪魚、洋蔥）', '7.00'), ('9. Insalata di mare', '海鮮沙拉（生菜、番茄、芝麻葉、蝦）', '7.00'),
   ('10. Greca', '希臘沙拉（有菲達起司）', '7.00'), ('11. Insalata nuggets di pollo', '雞塊沙拉', '7.00')])],
 ['海鮮麵 Di mare', _r([('12. Bigoli ai frutti di mare', '海鮮粗麵', '9.00'), ('13. Bigoli tonno olive capperi', '鮪魚橄欖酸豆粗麵', '9.00'),
   ('14. Cornetti rucola pomodorini gamberi', '芝麻葉小番茄鮮蝦短麵', '9.00'), ('15. Bigoli mare e monti', '海陸粗麵（海鮮＋菇類）', '9.00'),
   ('16. Cornetti gamberi e zucchine', '鮮蝦櫛瓜短麵', '9.00'), ('17. Bigoli al nero di seppia', '墨魚汁粗麵', '9.00'),
   ('18. Bigoli in salsa (piatto veneziano)', '洋蔥鯷魚醬粗麵（威尼斯傳統菜）', '9.00')])],
 ['陸上麵 Di terra', _r([('19. Bigoli all\'amatriciana', '阿瑪翠斯番茄培根粗麵', '9.00'), ('20. Bigoli aglio olio peperoncino', '蒜香辣椒橄欖油粗麵', '7.50'),
   ('21. Cornetti all\'arrabbiata', '香辣番茄短麵', '7.50'), ('22. Bigoli al pomodoro', '番茄粗麵', '7.50'), ('23. Cornetti funghi e speck', '蘑菇煙燻火腿短麵', '9.00'),
   ('24. Tortellini panna e prosciutto', '奶油火腿義大利餃', '9.00'), ('25. Bigoli alla carbonara', '培根蛋黃粗麵', '9.00'), ('26. Bigoli alla bolognese', '波隆那肉醬粗麵', '9.00'),
   ('27. Cornetti al pesto', '青醬短麵', '8.00'), ('28. Bigoli Alfredo – funghi, panna, grana', '阿弗雷多白醬粗麵（蘑菇、奶油、帕達諾起司）', '9.00')])],
 ['飲料 Drinks', _r([('Coca-Cola, Fanta, Sprite 33 cl', '可樂、芬達、雪碧', '2.50'), ('Coca-Cola Zero, Tè pesca/limone 450 ml', '零卡可樂、水蜜桃／檸檬紅茶', '3.00'),
   ('Birra Moretti 33 cl', '摩雷蒂啤酒（小）', '3.00'), ('Birra Moretti 66 cl', '摩雷蒂啤酒（大）', '4.00'), ('Acqua 500 ml', '礦泉水', '1.50'), ('Prosecco 20 cl', '普羅賽克氣泡酒', '4.00')])],
]
MENU_NOTE = ['Bigoli 是威尼斯的粗圓麵；Cornetti 是彎角形的短麵。', '照 Google 地圖上的菜單照片翻譯，價格以現場為準。']
