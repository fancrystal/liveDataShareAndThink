from app.core.config import Settings
from app.generation.deepseek_adapter import DeepSeekGenerationError
from app.generation.ports import GeneratedContent, GenerationBrief


class FailingDeepSeek:
    name = "deepseek:test"

    def generate(self, _brief: GenerationBrief) -> list[GeneratedContent]:
        raise DeepSeekGenerationError("temporary failure")


class TemplateFallback:
    name = "fixture-template-v1"

    def generate(self, _brief: GenerationBrief) -> list[GeneratedContent]:
        return []


def test_fallback_generator_uses_template_when_deepseek_fails() -> None:
    from app.generation.fallback_adapter import FallbackGenerator

    generator = FallbackGenerator(FailingDeepSeek(), TemplateFallback())

    assert generator.name == "deepseek:test->fixture-template-v1"
    assert generator.generate(_brief()) == []


def test_factory_keeps_template_only_when_explicitly_configured() -> None:
    from app.generation.factory import build_content_generator
    from app.generation.template_adapter import TemplateGenerator

    generator = build_content_generator(Settings(generation_provider="template", deepseek_api_key="available"))

    assert isinstance(generator, TemplateGenerator)


def _brief() -> GenerationBrief:
    return GenerationBrief(
        topic="topic",
        audience="audience",
        goal="live_preview",
        angle="angle",
        brand_tone="tone",
        forbidden_terms=(),
        evidence_summaries=(),
    )
