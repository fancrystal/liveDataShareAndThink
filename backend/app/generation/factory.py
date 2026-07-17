from app.core.config import Settings
from app.generation.deepseek_adapter import DeepSeekGenerator
from app.generation.fallback_adapter import FallbackGenerator
from app.generation.ports import ContentGenerator
from app.generation.template_adapter import TemplateGenerator


def build_content_generator(settings: Settings) -> ContentGenerator:
    if settings.generation_provider == "template":
        return TemplateGenerator()
    if settings.deepseek_api_key:
        return FallbackGenerator(
            DeepSeekGenerator(
                api_key=settings.deepseek_api_key,
                model=settings.deepseek_model,
                base_url=settings.deepseek_base_url,
            ),
            TemplateGenerator(),
        )
    return TemplateGenerator()
