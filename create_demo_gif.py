from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


OUTPUT_DIR = Path("assets")
OUTPUT_DIR.mkdir(exist_ok=True)
OUTPUT_PATH = OUTPUT_DIR / "rag_demo_output.gif"

WIDTH, HEIGHT = 1280, 720
BG = (247, 249, 252)
INK = (21, 31, 45)
MUTED = (87, 99, 116)
BLUE = (36, 99, 235)
GREEN = (22, 163, 74)
PANEL = (255, 255, 255)
LINE = (220, 226, 235)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


TITLE = font(44, True)
H2 = font(30, True)
BODY = font(24)
SMALL = font(19)
MONO = font(21)


def rounded(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], fill, outline=LINE, radius=14):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=1)


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font_obj, max_width: int) -> list[str]:
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        line = ""
        for word in words:
            candidate = f"{line} {word}".strip()
            if draw.textlength(candidate, font=font_obj) <= max_width:
                line = candidate
            else:
                if line:
                    lines.append(line)
                line = word
        if line:
            lines.append(line)
    return lines


def draw_text_block(draw, x, y, text, font_obj, color, max_width, line_gap=8):
    for line in wrap_text(draw, text, font_obj, max_width):
        draw.text((x, y), line, font=font_obj, fill=color)
        y += font_obj.size + line_gap
    return y


def base_frame(title: str, subtitle: str) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, WIDTH, 86), fill=(15, 23, 42))
    draw.text((48, 22), title, font=TITLE, fill=(255, 255, 255))
    draw.text((50, 104), subtitle, font=BODY, fill=MUTED)
    return image, draw


def frame_architecture() -> Image.Image:
    image, draw = base_frame(
        "RAG Knowledge Assistant",
        "Documents become searchable knowledge, then the model answers with citations.",
    )
    steps = [
        ("1", "Upload docs", "Markdown, text, PDF"),
        ("2", "Embed chunks", "OpenAI embeddings"),
        ("3", "Retrieve evidence", "Cosine similarity"),
        ("4", "Generate answer", "Grounded citations"),
    ]
    x = 64
    for number, heading, detail in steps:
        rounded(draw, (x, 230, x + 250, 470), PANEL)
        draw.ellipse((x + 88, 260, x + 162, 334), fill=BLUE)
        draw.text((x + 114, 276), number, font=H2, fill=(255, 255, 255))
        draw.text((x + 34, 360), heading, font=H2, fill=INK)
        draw.text((x + 34, 410), detail, font=BODY, fill=MUTED)
        x += 300
    draw.text((64, 590), "Built with Python, Streamlit, OpenAI, NumPy, and pypdf", font=BODY, fill=INK)
    return image


def frame_app() -> Image.Image:
    image, draw = base_frame(
        "Interactive Streamlit Demo",
        "A recruiter can upload documents, rebuild the index, ask questions, and inspect evidence.",
    )
    rounded(draw, (70, 165, 410, 640), PANEL)
    draw.text((100, 195), "Knowledge Base", font=H2, fill=INK)
    draw.text((100, 255), "Upload files", font=BODY, fill=MUTED)
    rounded(draw, (100, 295, 380, 360), (239, 246, 255), outline=(147, 197, 253))
    draw.text((130, 314), "company_notes.md", font=MONO, fill=BLUE)
    rounded(draw, (100, 410, 380, 475), BLUE, outline=BLUE)
    draw.text((145, 429), "Rebuild Index", font=BODY, fill=(255, 255, 255))
    draw.text((100, 535), "Retrieved chunks: 3", font=BODY, fill=MUTED)

    rounded(draw, (460, 165, 1210, 640), PANEL)
    draw.text((500, 195), "Ask a Question", font=H2, fill=INK)
    rounded(draw, (500, 255, 1160, 320), (248, 250, 252))
    draw.text((528, 274), "What does Acme Learning do?", font=BODY, fill=INK)
    rounded(draw, (500, 355, 1160, 520), (240, 253, 244), outline=(134, 239, 172))
    answer = "Acme Learning is a small education technology company that helps teams create internal knowledge bases."
    draw_text_block(draw, 528, 382, answer, BODY, INK, 580)
    draw.text((528, 480), "[company_notes.md:1]", font=SMALL, fill=GREEN)
    return image


def frame_result() -> Image.Image:
    image, draw = base_frame(
        "Result Output",
        "The answer is grounded in the uploaded document, and the source is visible.",
    )
    rounded(draw, (75, 165, 1205, 615), PANEL)
    draw.text((115, 205), "Question", font=H2, fill=INK)
    draw.text((115, 260), "What support do enterprise customers receive?", font=BODY, fill=MUTED)
    draw.line((115, 330, 1165, 330), fill=LINE, width=2)
    draw.text((115, 375), "Answer", font=H2, fill=INK)
    answer = "Enterprise customers receive a dedicated onboarding call and quarterly success review."
    draw_text_block(draw, 115, 430, answer, BODY, INK, 920)
    rounded(draw, (115, 525, 420, 575), (240, 253, 244), outline=(134, 239, 172))
    draw.text((140, 538), "Source: company_notes.md:1", font=SMALL, fill=GREEN)
    return image


def frame_takeaways() -> Image.Image:
    image, draw = base_frame(
        "What I Learned",
        "The project connects retrieval, embeddings, and LLM generation into one usable AI workflow.",
    )
    bullets = [
        "RAG improves answers by giving the model relevant private context.",
        "Chunking and retrieval quality directly affect answer quality.",
        "Citations and similarity scores make GenAI outputs easier to trust.",
        "A simple UI makes the project easier for recruiters to understand.",
    ]
    y = 190
    for bullet in bullets:
        draw.ellipse((90, y + 8, 108, y + 26), fill=BLUE)
        y = draw_text_block(draw, 135, y, bullet, BODY, INK, 980, line_gap=12) + 28
    draw.text((90, 610), "GitHub: github.com/mariapreethi-12/small-rag-genai-project", font=BODY, fill=BLUE)
    return image


frames = [
    frame_architecture(),
    frame_app(),
    frame_result(),
    frame_takeaways(),
]

durations = [1800, 2200, 2200, 2200]
frames[0].save(
    OUTPUT_PATH,
    save_all=True,
    append_images=frames[1:],
    duration=durations,
    loop=0,
    optimize=True,
)
print(OUTPUT_PATH.resolve())
