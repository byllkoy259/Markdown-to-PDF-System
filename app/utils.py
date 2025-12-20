import unicodedata
import re

def slugify(text: str) -> str:
    """
    Chuyển đổi chuỗi sang dạng slug dùng cho tên file/folder.
    """
    if not text:
        return "Unknown"
    
    # Chuẩn hóa Unicode
    text = unicodedata.normalize('NFKD', text)

    # Loại bỏ các ký tự dấu
    text = text.encode('ascii', 'ignore').decode('utf-8')

    # Chuyển thành chữ thường (tuỳ chọn)
    # text = text.lower()
    
    # Thay thế các ký tự không phải chữ/số thành gạch dưới
    text = re.sub(r'[^\w\s-]', '', text).strip()
    text = re.sub(r'[-\s]+', '_', text)
    
    return text or "Unknown"