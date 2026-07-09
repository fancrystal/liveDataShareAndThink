from app.generation.ports import GeneratedContent, GenerationBrief


class TemplateGenerator:
    @property
    def name(self) -> str:
        return "fixture-template-v1"

    def generate(self, brief: GenerationBrief) -> list[GeneratedContent]:
        goal_text = {
            "live_preview": "直播前先收藏，现场一起拆解",
            "live_booking": "预约直播，现场给你完整清单",
            "post_live_followup": "错过直播也能照着这份清单复盘",
        }[brief.goal]
        return [
            GeneratedContent(
                variant="practical",
                title="敏感肌先做减法",
                body=f"如果你是{brief.audience}，先别急着叠加产品。\n\n{brief.angle}：第一步记录刺激来源，第二步保留基础清洁和保湿。\n\n{goal_text}。",
                tags=("敏感肌", "护肤避坑", "直播预告"),
                cover_text="敏感肌先做减法",
            ),
            GeneratedContent(
                variant="story",
                title="我也曾经越护肤越红",
                body=f"以前一泛红我就换产品，结果越换越乱。后来我开始{brief.angle}，皮肤状态终于变得可判断。\n\n如果你也是{brief.audience}，{goal_text}。",
                tags=("敏感肌日记", "真实护肤", "直播预告"),
                cover_text="越护肤越红？",
            ),
            GeneratedContent(
                variant="contrarian",
                title="泛红时别急着修护",
                body=f"泛红时最危险的动作，可能不是少涂，而是继续加码。\n\n针对{brief.audience}，我更建议{brief.angle}。\n\n{goal_text}。",
                tags=("敏感肌", "反常识护肤", "直播预告"),
                cover_text="先停，再修护",
            ),
        ]

