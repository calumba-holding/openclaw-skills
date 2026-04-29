# 🚀 SPIN 销售法流程模拟脚本 (State Machine v2.0)
# 这是一个用于演示 SPIN 销售流程的进阶脚本。它实现了状态管理，允许流程在各个阶段之间灵活切换（特别是异议处理）。

import time
import sys

# 全局状态定义，用于控制流程的当前节点
class FlowState:
    START = 'START'
    SITUATION = 'SITUATION'
    PROBLEM = 'PROBLEM'
    IMPLICATION = 'IMPLICATION'
    NEED_PAYOFF = 'NEED_PAYOFF'
    OBJECTION = 'OBJECTION'
    COMPLETE = 'COMPLETE'

def print_header(title, module):
    """打印带模块名称的头部提示，增强用户体验。"""
    print("\n" + "="*60)
    print(f"🔥 当前流程状态：【{module}】")
    print(f"💡 任务阶段：{title}")
    print("="*60)

def run_opening_script():
    """阶段 0: 破冰与建立信任 (Opening Script)"""
    print("\n*** [模块: 开场白] ***")
    print("【流程提示】在正式进入 S-P-I-N 循环前，必须先完成破冰。请使用『Opening Scripts Library』中的策略进行开场，目标是让客户放下警惕心。")
    input(">>> 模拟开场白流程并接收客户初步反馈... (按 Enter 继续)")

def run_s_stage():
    """阶段 1: 现状问题 (Situation)"""
    print_header("S - 现状问题 (Situation)", "SITUATION")
    print("【目标】收集客观事实。必须基于事实提问，不能带任何评判色彩。")
    print("（参考：references/s-questions.md）")
    print("⭐ 示例：您目前使用的CRM系统是哪个版本？数据同步流程涉及哪些部门？")
    input(">>> 模拟提问，并接收客户对流程现状的描述... (按 Enter 继续)")

def run_p_stage():
    """阶段 2: 问题问题 (Problem)"""
    print_header("P - 问题问题 (Problem)", "PROBLEM")
    print("【目标】从客户陈述的S阶段事实中，挖掘出流程上的‘痛点’和‘不完美之处’。")
    print("（参考：references/p-questions.md）")
    print("⭐ 示例：基于您提到数据同步流程涉及三个部门，流程本身的耗时是否会造成人员效率瓶颈？")
    input(">>> 模拟挖掘痛点，将问题具象化，引发客户共鸣... (按 Enter 继续)")

def run_i_stage():
    """阶段 3: 影响问题 (Implication)"""
    print_header("I - 影响问题 (Implication)", "IMPLICATION")
    print("【目标】这是最关键的一步！必须将‘痛点’提升到‘业务风险’的高度。让客户感受到‘如果不解决，后果有多严重’。")
    print("（参考：references/i-questions.md）")
    print("⭐ 示例：如果数据同步的延迟是每月两次，这累计的资源浪费，是否已经影响到季度KPI的达成？")
    input(">>> 模拟后果推理，引导客户自我得出‘问题必须解决’的结论... (按 Enter 继续)")

def run_n_stage():
    """阶段 4: 需求-收益问题 (Need-Payoff)"""
    print_header("N - 需求-收益问题 (Need-Payoff)", "NEED_PAYOFF")
    print("【目标】将客户的焦虑（Pain）转化为对“解决方案带来的价值”（Gain）。让客户开口说出解决方案的好处。")
    print("（参考：references/n-questions.md）")
    print("⭐ 示例：如果这个问题能被实时解决，您认为这对您的团队能节省出多少周的人工时间，这能投入到更重要的哪个项目上？")
    input(">>> 模拟引导客户描述价值和可量化的收益... (按 Enter 结束流程)")

def run_objection_handling(state_name):
    """处理流程中断的异常状态：异议处理"""
    print("\n" + "#"*60)
    print(f"🚨 🚨 捕获到异议！当前的S-P-I-N流程被迫中断，进入【异常处理模块】🚨 🚨")
    print("流程状态被置于：OBJECTION")
    print("【指导】请参考 references/objections.md，记住：不反驳，而是'接纳 -> 澄清 -> 重述价值'。")
    
    # 1. 接纳
    input(">>> 步骤 1: 倾听与认可异议（例：承认预算确实是个痛点）... (按 Enter 继续)")
    # 2. 澄清
    input(">>> 步骤 2: 澄清异议（例：追问，是预算还是ROI？）... (按 Enter 继续)")
    # 3. 重述价值
    input(">>> 步骤 3: 重述价值，并将话题拉回核心痛点（I/P阶段的成果）。 (按 Enter 继续)")
    
    # 流程恢复
    print("\n✅ 异议处理完毕，流程得以恢复。系统状态：[RESTORED]")
    # 在实际应用中，这里需要一个机制让调用方知道需要重新运行哪个阶段。
    # 我们在此模拟恢复到上一个未完成的阶段。
    # 由于脚本限制，当前我们简单地提示用户：
    print("流程已恢复。请根据您处理异议的内容，确定当前最需要强化的阶段，从该阶段开始继续。")
    
def main_interview_loop():
    """主流程状态机控制函数"""
    current_state = FlowState.START
    
    while current_state != FlowState.COMPLETE:
        if current_state == FlowState.START:
            # Step 1: 启动流程
            run_opening_script()
            current_state = FlowState.SITUATION # 默认从S开始
        
        elif current_state == FlowState.SITUATION:
            run_s_stage()
            current_state = FlowState.PROBLEM # S -> P
        
        elif current_state == FlowState.PROBLEM:
            run_p_stage()
            # 在实际交互中，这是最容易产生异议的地方。
            # 这里增加了一个判断：如果用户在P阶段提出预算或功能异议，需要跳转。
            print("\n【状态检查点】在P阶段，如果用户提出价格或功能异议，请立即调用【异议处理】流程。")
            # 假设流程正常继续：
            current_state = FlowState.IMPLICATION # P -> I
        
        elif current_state == FlowState.IMPLICATION:
            run_i_stage()
            # 关键点：I阶段的发现（客户意识到问题严重性）是进入 N 阶段的完美垫脚石。
            current_state = FlowState.NEED_PAYOFF # I -> N
            
        elif current_state == FlowState.NEED_PAYOFF:
            run_n_stage()
            # 流程结束
            current_state = FlowState.COMPLETE
            
        # --- 状态机循环结束 ---
        
    print("\n===========================================================")
    print("✅ 恭喜！您已成功运行 SPIN 流程的完整模拟。流程圆满结束。")
    print("===========================================================")

if __name__ == "__main__":
    main_interview_loop()
