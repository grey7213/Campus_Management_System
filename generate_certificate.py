from PIL import Image, ImageDraw, ImageFont
import os

# Create certificate image
width, height = 1000, 700
image = Image.new('RGB', (width, height), color='white')
draw = ImageDraw.Draw(image)

# Add border
border_width = 20
draw.rectangle(
    [(border_width, border_width), (width - border_width, height - border_width)],
    outline=(44, 62, 80),  # Dark blue
    width=5
)

# Add fancy background pattern
for i in range(20, width - 20, 40):
    for j in range(20, height - 20, 40):
        draw.ellipse((i, j, i + 5, j + 5), fill=(230, 230, 230))

# Add certificate title
try:
    # Try to use a Chinese font if available
    title_font = ImageFont.truetype("simhei.ttf", 48)
    text_font = ImageFont.truetype("simhei.ttf", 24)
    name_font = ImageFont.truetype("simhei.ttf", 36)
except IOError:
    # Fallback to default font
    title_font = ImageFont.load_default()
    text_font = ImageFont.load_default()
    name_font = ImageFont.load_default()

# Add certificate header
title_text = "计算机二级证书"
title_width = draw.textlength(title_text, font=title_font)
draw.text(
    ((width - title_width) // 2, 80),
    title_text,
    font=title_font,
    fill=(44, 62, 80)  # Dark blue
)

# Add certificate type
type_text = "专业能力证书"
type_width = draw.textlength(type_text, font=text_font)
draw.text(
    ((width - type_width) // 2, 150),
    type_text,
    font=text_font,
    fill=(52, 152, 219)  # Blue
)

# Add horizontal line
draw.line([(100, 200), (width - 100, 200)], fill=(52, 152, 219), width=2)

# Add certificate content
content_text = "兹证明"
content_width = draw.textlength(content_text, font=text_font)
draw.text(
    ((width - content_width) // 2, 250),
    content_text,
    font=text_font,
    fill=(0, 0, 0)
)

# Add recipient name
name_text = "杜聪"
name_width = draw.textlength(name_text, font=name_font)
draw.text(
    ((width - name_width) // 2, 300),
    name_text,
    font=name_font,
    fill=(231, 76, 60)  # Red
)

# Add student ID
student_id_text = "学号: 20240004"
student_id_width = draw.textlength(student_id_text, font=text_font)
draw.text(
    ((width - student_id_width) // 2, 350),
    student_id_text,
    font=text_font,
    fill=(85, 85, 85)
)

# Add description
description_text = [
    "该学生在Java程序设计课程中表现优异，熟练掌握Java语言基础知识",
    "和面向对象编程思想，能够独立设计和实现中等规模的Java应用程序，",
    "熟悉常用设计模式和框架的应用，编程风格良好，代码结构清晰，",
    "具有较强的问题分析和解决能力。"
]

for i, line in enumerate(description_text):
    line_width = draw.textlength(line, font=text_font)
    draw.text(
        ((width - line_width) // 2, 400 + i * 30),
        line,
        font=text_font,
        fill=(85, 85, 85)
    )

# Add horizontal line
draw.line([(100, 550), (width - 100, 550)], fill=(238, 238, 238), width=1)

# Add date and signature
draw.text(
    (100, 580),
    "颁发日期: 2024年04月11日",
    font=text_font,
    fill=(85, 85, 85)
)

# draw.text(
#     (width - 250, 580),
#     "校长: 张明",
#     font=text_font,
#     fill=(85, 85, 85)
# )

# Add certificate ID at the bottom
cert_id_text = "证书编号: 0x3db5ced3ced84ea6b4c3ec808610b698"
cert_id_width = draw.textlength(cert_id_text, font=ImageFont.load_default())
draw.text(
    ((width - cert_id_width) // 2, height - 50),
    cert_id_text,
    font=ImageFont.load_default(),
    fill=(136, 136, 136)
)

# Create directory if it doesn't exist
os.makedirs("app/static/uploads/certificates", exist_ok=True)

# Save the image
image_path = "app/static/uploads/certificates/cert_java_20240004.png"
image.save(image_path)

print(f"Certificate generated and saved to {image_path}") 