import json

with open('../data/books/books.json', 'r', encoding='utf-8') as f:
    books = json.load(f)

print(f"JSON 大小: {len(json.dumps(books, ensure_ascii=False)):,} 字节")
print(f"总书目: {len(books)} 本")
print(f"第一本: {books[0]['title']} - {books[0]['author']}")
print(f"最后一本: {books[-1]['title']} - {books[-1]['author']}")

required = ['id', 'isbn', 'title', 'author', 'publisher', 'publish_year', 'category', 'location', 'shelf_number', 'stock', 'available', 'tags']
all_ok = True
for i, b in enumerate(books):
    for k in required:
        if k not in b:
            print(f"第 {i+1} 本书缺少字段: {k}")
            all_ok = False
if all_ok:
    print("所有字段完整")

# 统计分类
from collections import Counter
cat_counts = Counter(b["category"] for b in books)
print("\n=== 分类统计 ===")
for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1]):
    print(f"  {cat}: {count} 本")
