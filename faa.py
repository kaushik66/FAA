# faa.py
import argparse
from openai import OpenAI
from config import OPENAI_API_KEY
from agents.orchestrator import orchestrator_agent
from agents.rga_agent import rga_agent
from agents.detective_agent import detective_agent
from tools.sql_tools import run_sql_query
from tools.plot_tools import plot_transaction_timeline
from utils.llm import parse_llm_json
from agents.vision_agent import vision_agent

client = OpenAI(api_key=OPENAI_API_KEY)

def run_faa(case_id: str, max_steps: int = 3, return_verdict: bool = False):
    print(f"🚀 Starting FAA investigation for Case: {case_id}")

    investigation_log = []
    step = 0
    stop_flag = False

    while not stop_flag and step < max_steps:
        print(f"\n🌀 Step {step+1}")

        # ---- Orchestrator decides next action ----
        # Pass case_id safely as parameter rather than raw string concatenation
        trimmed_log = investigation_log[-5:]
        plan = orchestrator_agent(client, case_id, trimmed_log)
        print(f"Plan: {plan}")

        if plan.get("stop", False):
            stop_flag = True
            break

        # ---- Execute tool ----
        tool = plan.get("tool")
        if tool == "sql":
            query = plan.get("query")
            params = plan.get("params", None)
            result = run_sql_query(query, params=params)
            # Convert DataFrame to serializable form if applicable
            if hasattr(result, "to_dict"):
                display_result = result.head(10).to_dict(orient="records")
            else:
                display_result = result
            investigation_log.append({"step": step, "tool": "sql", "query": query, "result": display_result})
            try:
                print(result.head(5).to_string())
            except Exception:
                print(str(result)[:200])

        elif tool == "plot":
            tx_id = plan["trans_num"]
            plot_path = plot_transaction_timeline(tx_id)

            # 👁️ Vision Agent reads the plot
            vision_obs = vision_agent(client, plot_path)

            investigation_log.append({
                "step": step,
                "tool": "plot",
                "trans_num": tx_id,
                "plot_path": plot_path,
                "vision_analysis": vision_obs,
                "notes_for_rga": plan.get("notes_for_rga", "")
            })

        else:
            print("⚠️ Unknown tool requested by orchestrator.")
            stop_flag = True

        step += 1

    # ---- RGA Agent: Summarize investigation ----
    print("\n📝 Generating investigation report...")
    report, key_evidence = rga_agent(client, investigation_log)

    # ---- Detective Agent: Final verdict ----
    print("\n🔍 Making final verdict...")
    result = detective_agent(client, key_evidence)
    verdict = result.get("verdict")
    confidence = result.get("confidence")

    if return_verdict:
        return verdict, confidence

    print("\n✅ Investigation Complete!")
    print("Report:", report)
    print("Verdict:", verdict)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--case_id", type=str, required=True, help="Transaction or case ID to investigate")
    parser.add_argument("--max_steps", type=int, default=3, help="Max reasoning steps")
    args = parser.parse_args()

    run_faa(case_id=args.case_id, max_steps=args.max_steps)