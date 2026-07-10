from app.core.config import Settings
from app.generation.deepseek_adapter import DeepSeekGenerator
from app.generation.ports import ContentGenerator
from app.generation.template_adapter import TemplateGenerator


def build_content_generator(settings: Settings) -> ContentGenerator:
    if settings.generation_provider == "template":
        return TemplateGenerator()
    if settings.generation_provider == "deepseek" and not settings.deepseek_api_key:
        raise RuntimeError("DEEPSEEK_API_KEY is required when GENERATION_PROVIDER=deepseek")
    if settings.deepseek_api_key:
        return DeepSeekGenerator(
            api_key=settings.deepseek_api_key,
            model=settings.deepseek_model,
            base_url=settings.deepseek_base_url,
        )
    return TemplateGenerator()
