import mistune
from mistune.renderers.html import HTMLRenderer
import matplotlib.pyplot as plt
import io
import base64

# Cấu hình Matplotlib để vẽ công thức toán
plt.rcParams.update({
    "text.usetex": False,
    "mathtext.fontset": "cm",
})

def latex_to_base64_image(latex_str, fontsize=12, color='black'):
    """
    Hàm vẽ chuỗi LaTeX thành ảnh PNG trong suốt và trả về chuỗi Base64.
    """
    try:
        fig = plt.figure(figsize=(0.1, 0.1))
        
        clean_latex = latex_str.strip('$')
        text = f"${clean_latex}$"
        
        fig.text(0, 0, text, fontsize=fontsize, color=color)
        
        buffer = io.BytesIO()
        
        fig.savefig(buffer, format='png', transparent=True, dpi=200, bbox_inches='tight', pad_inches=0.02)
        plt.close(fig)
        
        buffer.seek(0)
        img_str = base64.b64encode(buffer.read()).decode('utf-8')
        return f"data:image/png;base64,{img_str}"
    except Exception as e:
        print(f"Error rendering math: {e}")
        return None

class MathImageRenderer(HTMLRenderer):
    """
    Custom Renderer: Biến LaTeX thành thẻ <img> thay vì text.
    """
    def inline_math(self, text):
        img_src = latex_to_base64_image(text, fontsize=14)
        if img_src:
            return f'<img src="{img_src}" alt="{text}" style="vertical-align: -20%; height: 1.2em;" class="math-inline" />'
        return f'<span class="math-error">\\({text}\\)</span>'

    def block_math(self, text):
        img_src = latex_to_base64_image(text, fontsize=18)
        if img_src:
            return f'<div class="math-block" style="text-align: center; margin: 1em 0;"><img src="{img_src}" alt="{text}" /></div>'
        return f'<div class="math-error">$${text}$$</div>'

class MarkdownConverter:
    def __init__(self):
        self.markdown = mistune.create_markdown(
            renderer=MathImageRenderer(),
            plugins=[
                'table', 
                'url', 
                'task_lists', 
                'strikethrough', 
                'footnotes', 
                'math'
            ]
        )

    def convert_to_html(self, content: str) -> str:
        if not content:
            return ""
        return self.markdown(content)

converter_service = MarkdownConverter()