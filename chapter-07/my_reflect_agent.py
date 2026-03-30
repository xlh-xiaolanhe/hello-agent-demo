from typing import Optional, Dict
from hello_agents import HelloAgentsLLM

import os
os.environ["NO_PROXY"] = "*"

# 默认的反思提示词字典
DEFAULT_PROMPTS = {
    "initial": """请根据以下要求完成任务:\n任务: {task}\n请提供一个完整、准确的回答。""",
    "reflect": """请仔细审查以下回答，并找出可能的问题或改进空间:\n# 原始任务:\n{task}\n# 当前回答:\n{content}\n请分析这个回答的质量，指出不足之处，并提出具体的改进建议。\n如果回答已经很好，请直接回答"无需改进"。""",
    "refine": """请根据反馈意见改进你的回答:\n# 原始任务:\n{task}\n# 上一轮回答:\n{last_attempt}\n# 反馈意见:\n{feedback}\n请提供一个改进后的回答。"""
}

class MyReflectionAgent:
    def __init__(
        self,
        name: str,
        llm: HelloAgentsLLM,
        max_steps: int = 3,
        custom_prompts: Optional[Dict[str, str]] = None
    ):
        self.name = name
        self.llm = llm
        self.max_steps = max_steps
        
        self.prompts = DEFAULT_PROMPTS.copy()
        if custom_prompts:
            self.prompts.update(custom_prompts)
            
        print(f"✅ {self.name} 初始化完成，最大反思轮数: {self.max_steps}")

    def run(self, input_text: str, **kwargs) -> str:
        print(f"\n🤖 {self.name} 开始处理任务: {input_text}")
        
        # 1. 生成初稿
        print("\n--- 正在生成初稿 ---")
        initial_prompt = self.prompts["initial"].format(task=input_text)
        current_draft = self.llm.invoke([{"role": "user", "content": initial_prompt}], **kwargs)
        print(f"初稿内容预览: {current_draft[:50]}...")
        
        # 2. 进入反思与修改循环
        for step in range(1, self.max_steps + 1):
            print(f"\n--- 🔍 第 {step} 轮反思 ---")
            
            # 步骤 A: 提取反馈
            reflect_prompt = self.prompts["reflect"].format(
                task=input_text, 
                content=current_draft
            )
            feedback = self.llm.invoke([{"role": "user", "content": reflect_prompt}], **kwargs)
            print(f"反思意见: {feedback[:50]}...")
            
            # 步骤 B: 检查是否需要提前结束
            if "无需改进" in feedback:
                print("✨ 完美通过自我审查，结束打磨！")
                break
                
            # 步骤 C: 根据反馈进行修改
            print(f"--- ✍️ 正在根据反馈进行第 {step} 轮修改 ---")
            refine_prompt = self.prompts["refine"].format(
                task=input_text,
                last_attempt=current_draft,
                feedback=feedback
            )
            current_draft = self.llm.invoke([{"role": "user", "content": refine_prompt}], **kwargs)
            
        print("\n✅ 最终输出完成！")
        return current_draft