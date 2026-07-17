from app.generation.deepseek_adapter import DeepSeekGenerationError
from app.generation.ports import ContentGenerator, GeneratedContent, GenerationBrief


class FallbackGenerator:
    """Uses a deterministic generator only when a DeepSeek request fails safely."""

    def __init__(self, primary: ContentGenerator, fallback: ContentGenerator) -> None:
        self.primary = primary
        self.fallback = fallback
        self.last_generator_name = primary.name

    @property
    def name(self) -> str:
        return f"{self.primary.name}->{self.fallback.name}"

    def generate(self, brief: GenerationBrief) -> list[GeneratedContent]:
        try:
            generated = self.primary.generate(brief)
            self.last_generator_name = self.primary.name
            return generated
        except DeepSeekGenerationError:
            self.last_generator_name = self.fallback.name
            return self.fallback.generate(brief)
