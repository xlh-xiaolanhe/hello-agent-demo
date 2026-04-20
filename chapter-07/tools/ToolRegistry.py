"""工具注册表 - HelloAgents原生工具系统"""
from typing import Any, Callable, Optional, Dict, List
from .Tool import Tool
from .ToolParameter import ToolParameter

class ToolRegistry:
    """
    HelloAgents 工具注册表

    提供工具的注册、管理和执行功能
    支持两种工具的注册方式：
    1. Tool对象注册(推荐)
    2. 函数直接注册 (简便)
    """

    def __init__(self):
        self.description = None
        self.name = None
        self._tools: dict[str, Tool] = {}
        self._functions: dict[str, dict[str, Any]] = {}

    def register_tool(self, tool: Tool):
        """
        注册Tool对象

        Args:
            tool: Tool 实例
        """
        if tool.name in self._tools:
            print(f"[WARNING] 警告：工具 '{tool.name}' 已存在，将被覆盖。")

        self._tools[tool.name] = tool
        print(f"[OK] 工具 '{tool.name}' 已注册。")

    def register_function(self, name: str, description: str, func: Callable[[str], str]):
        """
        直接注册函数作为工具（简便方式）

        Args:
            name: 工具名称
            description: 工具描述
            func: 工具函数，接受字符串参数，返回字符串结果
        """
        if name in self._functions:
            print(f"[WARNING] 警告：工具 '{name}' 已存在，将被覆盖。")

        self._functions[name] = {
            "description": description,
            "func": func
        }
        print(f"[OK] 工具 '{name}' 已注册。")


    def unregister(self, name: str):
        """注销工具"""
        if name in self._tools:
            del self._tools[name]
            print(f"[DELETE] 工具 '{name}' 已注销。")
        elif name in self._functions:
            del self._functions[name]
            print(f"[DELETE] 工具 '{name}' 已注销。")
        else:
            print(f"[WARNING] 工具 '{name}' 不存在。")


    def get_tool(self, name: str) -> Optional[Tool]:
        """获取Tool对象"""
        return self._tools.get(name)


    def get_function(self, name: str) -> Optional[Callable]:
        """获取工具函数"""
        func_info = self._functions.get(name)
        return func_info["func"] if func_info else None

    def execute_tool(self, name: str, input_text: str) -> str:
        """
        执行工具

        Args:
            name: 工具名称
            input_text: 输入参数

        Returns:
            工具执行结果
        """
        # 优先查找Tool对象
        if name in self._tools:
            tool = self._tools[name]
            try:
                # 简化参数传递，直接传入字符串
                return tool.run({"input": input_text})
            except Exception as e:
                return f"错误：执行工具 '{name}' 时发生异常: {str(e)}"

        # 查找函数工具
        elif name in self._functions:
            func = self._functions[name]["func"]
            try:
                return func(input_text)
            except Exception as e:
                return f"错误：执行工具 '{name}' 时发生异常: {str(e)}"

        else:
            return f"错误：未找到名为 '{name}' 的工具。"


    def get_tools_description(self) -> str:
        """获取所有可用工具的格式化描述字符串"""
        descriptions = []

        # Tool对象描述
        for tool in self._tools.values():
            descriptions.append(f"- {tool.name}: {tool.description}")

        # 函数工具描述
        for name, info in self._functions.items():
            descriptions.append(f"- {name}: {info['description']}")

        return "\n".join(descriptions) if descriptions else "暂无可用工具"

    def to_openai_schema(self) -> Dict[str, Any]:
        """转换为 OpenAI function calling schema 格式

        用于 FunctionCallAgent，使工具能够被 OpenAI 原生 function calling 使用

        Returns:
            符合 OpenAI function calling 标准的 schema
        """
        parameters = self.get_parameters()

        # 构建 properties
        properties = {}
        required = []

        for param in parameters:
            # 基础属性定义
            prop = {
                "type": param.type,
                "description": param.description
            }

            # 如果有默认值，添加到描述中（OpenAI schema 不支持 default 字段）
            if param.default is not None:
                prop["description"] = f"{param.description} (默认: {param.default})"

            # 如果是数组类型，添加 items 定义
            if param.type == "array":
                prop["items"] = {"type": "string"}  # 默认字符串数组

            properties[param.name] = prop

            # 收集必需参数
            if param.required:
                required.append(param.name)

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }
    
    
    def get_parameters(self) -> List[ToolParameter]:
        """汇总获取所有注册工具的参数"""
        all_parameters = []

        # 1. 遍历并提取标准 Tool 对象的参数
        for  tool_name, tool in self._tools.items():
            if hasattr(tool, 'get_parameters'):
                all_parameters.extend(tool.get_parameters())
        
        # 2. 为简便方式注册的纯函数生成对应的参数
        for func_name, func_info in self._functions.items():
            # 用 ToolParameter 包装它
            param = ToolParameter(
                name=f"{func_name}_query",  # 加上工具名前缀
                type="string",
                description=f"传递给 {func_name} 工具的输入内容",
                required=True,
                default=None
            )
            all_parameters.append(param)

        return all_parameters
    