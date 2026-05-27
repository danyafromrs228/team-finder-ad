import random
import re
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.paginator import Paginator


def generate_avatar(user):
    from .models import AVATAR_SIZE, AVATAR_FONT_SIZE, AVATAR_COLORS
    
    size = (AVATAR_SIZE, AVATAR_SIZE)
    color = random.choice(AVATAR_COLORS)

    image = Image.new("RGB", size, color)
    draw = ImageDraw.Draw(image)

    letter = user.name[0].upper() if user.name else "?"

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", AVATAR_FONT_SIZE)
    except:
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", AVATAR_FONT_SIZE)
        except:
            font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), letter, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    position = ((size[0] - text_width) / 2, (size[1] - text_height) / 2)

    draw.text(position, letter, fill="white", font=font)

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    user.avatar.save(f"avatar_{user.email}.png", ContentFile(buffer.read()), save=False)
    buffer.close()


def validate_phone_number(phone, instance=None):
    from .models import User
    
    if not phone:
        return phone

    if not re.match(r"^(\+7|8)?\d{10}$", phone):
        raise ValidationError("Номер телефона должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX")

    if phone.startswith("8"):
        phone = "+7" + phone[1:]

    user_id = instance.id if instance else None
    if User.objects.filter(phone=phone).exclude(id=user_id).exists():
        raise ValidationError("Пользователь с таким номером телефона уже существует")

    return phone


def validate_github_url(github_url):
    if github_url and "github.com" not in github_url:
        raise ValidationError("Ссылка должна вести на GitHub")
    return github_url


def paginate_queryset(request, queryset, page_size=12):
    paginator = Paginator(queryset, page_size)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)
