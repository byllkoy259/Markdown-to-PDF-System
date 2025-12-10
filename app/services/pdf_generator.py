from weasyprint import HTML, CSS, default_url_fetcher
from weasyprint.text.fonts import FontConfiguration
import logging
import requests
import re
from io import BytesIO
import pypdf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFGenerator:
    def __init__(self):
        self.font_config = FontConfiguration()

        common_css_rules = """
            /* NUCLEAR RESET - ÉP PHÔNG CHỮ SERIF CHO TOÀN BỘ VĂN BẢN */
            /* Dùng dấu * để chọn tất cả mọi thành phần */
            * {
                /* Thứ tự ưu tiên: 
                   1. Times New Roman (Windows/Mac chuẩn)
                   2. Liberation Serif (Linux chuẩn - giống hệt Times)
                   3. Nimbus Roman No9 L (Linux dự phòng)
                   4. DejaVu Serif (Linux dự phòng)
                   5. serif (Font có chân bất kỳ - Chặn tuyệt đối việc nhảy về Sans-serif) 
                */
                font-family: 'Times New Roman', 'Liberation Serif', 'Nimbus Roman No9 L', 'DejaVu Serif', serif !important;
            }

            /* Cấu hình body cụ thể */
            body {
                font-size: 13pt;
                line-height: 1.4;
                color: #000;
                text-align: justify;
            }

            /* XỬ LÝ IN ĐẬM VÀ TIÊU ĐỀ */
            strong, b {
                font-weight: bold !important;
                /* Font-family đã được xử lý bởi dấu * ở trên nên sẽ đồng bộ */
            }

            h1, h2, h3, h4, h5, h6 {
                font-weight: bold !important;
                font-style: normal !important; /* Không in nghiêng */
                margin-top: 20px;
                margin-bottom: 10px;
                page-break-after: avoid;
            }

            h1 { font-size: 24pt; text-transform: uppercase; text-align: center; margin-bottom: 30px; }
            h2 { font-size: 16pt; margin-top: 30px; margin-bottom: 15px; }
            h3 { font-size: 14pt; }

            /* GIỮ NGUYÊN FIX LỖI CĂN LỀ DẤU * */
            ul, ol {
                margin: 10px 0 15px 0;
                padding-left: 40px;
            }
            li {
                margin-bottom: 8px;
                list-style-position: outside !important;
                text-align: justify;
            }
            /* Gỡ bỏ margin của thẻ p bên trong li nếu có, nhưng không làm nó inline */
            li p { margin: 0; padding: 0; }
            /* Đảm bảo hình ảnh trong list vẫn là block để có thể căn lề */
            li img { display: block; }

            /* BLOCKQUOTE */
            blockquote {
                margin: 15px 0 15px 20px;
                padding: 10px 15px;
                border-left: 4px solid #ddd;
                background-color: #f9f9f9;
                color: #555;
            }

            /* CODE BLOCK & TABLE */
            pre {
                font-family: 'Courier New', 'Liberation Mono', monospace !important;
                font-size: 11pt;
                background-color: #f5f5f5;
                padding: 12px;
                border: 1px solid #ddd;
                white-space: pre-wrap; 
                word-wrap: break-word;
            }
            
            /* Inline code */
            code, span.code {
                font-family: 'Courier New', 'Liberation Mono', monospace !important;
                font-size: 0.9em; /* Hơi nhỏ hơn văn bản thường */
                background-color: #f0f0f0;
                padding: 2px 4px;
                border-radius: 3px;
            }

            table { width: 100%; border-collapse: collapse; margin: 20px 0; }
            th, td { border: 1px solid #000; padding: 8px; vertical-align: top; }
            img { max-width: 100%; height: auto; display: block; margin: 15px auto; }
            
            .text-danger, .title-danger { color: #FF0000 !important; }
            .text-center { text-align: center; }
            .row, .header-container { display: flex; justify-content: space-between; width: 100%; margin-bottom: 25px; }
        """

        # CSS cho trang có đánh số
        page_with_number_css = """
            @page {
                size: A4;
                margin: 2cm 2.5cm;
                @bottom-right {
                    content: "" counter(page) " / " counter(pages);
                    font-size: 10pt;
                    font-family: 'Times New Roman', 'Liberation Serif', 'Nimbus Roman No9 L', 'DejaVu Serif', serif;
                    color: #555;
                }
            }
        """

        # CSS cho trang không đánh số
        page_without_number_css = """
            @page {
                size: A4;
                margin: 2cm 2.5cm;
            }
        """

        self.default_css = CSS(string=page_with_number_css + common_css_rules, font_config=self.font_config)
        self.no_page_number_css = CSS(string=page_without_number_css + common_css_rules, font_config=self.font_config)

    @staticmethod
    def custom_url_fetcher(url):
        if url.startswith("http"):
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                return {
                    'string': response.content,
                    'mime_type': response.headers.get('Content-Type'),
                    'encoding': response.encoding,
                    'redirected_url': response.url,
                }
            except Exception as e:
                logger.error(f"Failed to fetch image {url}: {e}")
                return default_url_fetcher(url)
        return default_url_fetcher(url)

    def clean_html(self, html_content: str) -> str:
        # Gỡ thẻ <p> bên trong <li>: <li<...><p>content</p></li> -> <li<...>>content</li>
        # Regex này tìm các thẻ li, bắt lấy nội dung bên trong thẻ p và thay thế toàn bộ
        cleaned_html = re.sub(r'<li([^>]*)>\s*<p>(.*?)</p>\s*</li>', r'<li\1>\2</li>', html_content, flags=re.DOTALL)

        return cleaned_html

    def generate_pdf(self, html_content: str, show_page_number: bool = True) -> bytes:
        cleaned_html = self.clean_html(html_content)
        full_html_string = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Export PDF</title>
        </head>
        <body>
            {cleaned_html}
        </body>
        </html>
        """

        html = HTML(string=full_html_string, base_url=".", url_fetcher=self.custom_url_fetcher)

        stylesheet = self.default_css if show_page_number else self.no_page_number_css

        try:
            pdf_bytes = html.write_pdf(
                stylesheets=[stylesheet],
                font_config=self.font_config,
                presentational_hints=True
            )
            return pdf_bytes
        except Exception as e:
            logger.error(f"WeasyPrint error: {e}")
            raise e

    def merge_with_footer(self, body_pdf_bytes: bytes, footer_pdf_bytes: bytes) -> bytes:
        """
        Hợp nhất hai file PDF.
        Nội dung của trang cuối cùng trong 'body_pdf' sẽ được phủ lên trên
        trang đầu tiên của 'footer_pdf'.
        """
        try:
            body_io = BytesIO(body_pdf_bytes) # param body_pdf_bytes: Bytes của file PDF nội dung chính
            footer_io = BytesIO(footer_pdf_bytes) # param footer_pdf_bytes: Bytes của file PDF chứa footer

            body_reader = pypdf.PdfReader(body_io)
            writer = pypdf.PdfWriter()

            # Giữ lại metadata từ file gốc
            if body_reader.metadata:
                writer.add_metadata(body_reader.metadata)

            # Thêm tất cả các trang của body, trừ trang cuối cùng
            for page in body_reader.pages[:-1]:
                writer.add_page(page)

            # Nếu body PDF không có trang nào
            if not body_reader.pages:
                logger.warning("Body PDF is empty. Cannot perform merge.")
                # Trả về footer hoặc một PDF rỗng tùy theo yêu cầu logic
                with BytesIO() as final_io:
                    writer.write(final_io)
                    return final_io.getvalue()

            # Xử lý trang cuối cùng
            footer_reader = pypdf.PdfReader(footer_io)
            if not footer_reader.pages:
                logger.error("Footer PDF is empty. Cannot merge.")
                raise ValueError("Footer PDF has no pages and cannot be used for merging.")

            last_page_body = body_reader.pages[-1]
            footer_page_template = footer_reader.pages[0]

            # Phủ nội dung của trang cuối lên trên trang footer
            footer_page_template.merge_page(last_page_body)
            writer.add_page(footer_page_template)

            with BytesIO() as final_io:
                writer.write(final_io)
                return final_io.getvalue()
        except Exception as e:
            logger.error(f"PyPDF Error during merge: {e}")
            raise e

pdf_service = PDFGenerator()