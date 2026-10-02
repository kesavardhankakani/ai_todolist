from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
import os
import json


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

app = Flask(__name__)

api_key = os.getenv("GROQ_API_KEY")

print("========================================")
print("AI TODO LIST APPLICATION")
print("========================================")
print("GROQ API KEY FOUND:", bool(api_key))


# ============================================================
# GROQ CLIENT
# ============================================================

client = None

if api_key:
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1"
    )


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():
    return render_template("index.html")


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "api_key_configured": bool(api_key)
    })


# ============================================================
# AI TODO GENERATOR
# ============================================================

@app.route("/generate", methods=["POST"])
def generate():

    try:

        # ----------------------------------------------------
        # Check API configuration
        # ----------------------------------------------------

        if not api_key or client is None:
            return jsonify({
                "success": False,
                "error": "AI service is not configured. GROQ_API_KEY is missing."
            }), 500


        # ----------------------------------------------------
        # Read JSON request
        # ----------------------------------------------------

        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                "success": False,
                "error": "Invalid request. No data was received."
            }), 400


        # ----------------------------------------------------
        # Extract user input
        # ----------------------------------------------------

        goal = str(data.get("goal", "")).strip()
        deadline = str(data.get("deadline", "")).strip()
        priority = str(data.get("priority", "")).strip()


        # ----------------------------------------------------
        # Validate input
        # ----------------------------------------------------

        if not goal:
            return jsonify({
                "success": False,
                "error": "Please enter a goal."
            }), 400

        if len(goal) < 3:
            return jsonify({
                "success": False,
                "error": "Please enter a more detailed goal."
            }), 400

        if not deadline:
            return jsonify({
                "success": False,
                "error": "Please select a deadline."
            }), 400

        if not priority:
            return jsonify({
                "success": False,
                "error": "Please select a priority."
            }), 400


        # ----------------------------------------------------
        # Debug information
        # ----------------------------------------------------

        print("\n========================================")
        print("NEW AI TODO REQUEST")
        print("========================================")
        print("Goal:", goal)
        print("Deadline:", deadline)
        print("Priority:", priority)


        # ====================================================
        # AI PROMPT
        # ====================================================

        prompt = f"""
You are an expert productivity planner.

Your job is to convert a user's goal into a practical,
specific and achievable action plan.

USER GOAL:
{goal}

DEADLINE:
{deadline}

PRIORITY:
{priority}

Create a realistic plan that helps the user actually
achieve this goal.

RULES:

1. Generate between 8 and 10 tasks.

2. Every task must directly contribute to the goal.

3. Tasks must be specific and actionable.

4. Do not create vague tasks such as:
   - "Work on the goal"
   - "Start studying"
   - "Keep practicing"
   - "Do research"

5. Break large goals into smaller practical steps.

6. Arrange tasks in a logical order.

7. Consider the deadline when planning the tasks.

8. Consider the priority:
   - High = important and focused plan
   - Medium = balanced plan
   - Low = flexible plan

9. Make the plan realistic for one person.

10. Avoid unnecessary repetition.

11. Each task should be short and easy to understand.

12. Do not include task numbers.

13. Do not include Markdown.

14. Do not include explanations outside the JSON.

15. Return ONLY valid JSON.

The JSON must use exactly this structure:

{{
    "tasks": [
        "Specific actionable task 1",
        "Specific actionable task 2",
        "Specific actionable task 3"
    ]
}}
"""


        # ====================================================
        # CALL GROQ
        # ====================================================

        print("\nSending request to Groq...")


        response = client.chat.completions.create(

            model="openai/gpt-oss-120b",

            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional AI productivity "
                        "planner. Always return valid JSON."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.5,

            response_format={
                "type": "json_object"
            }
        )


        # ====================================================
        # READ AI RESPONSE
        # ====================================================

        if not response.choices:
            raise ValueError("AI returned no response.")


        ai_response = response.choices[0].message.content


        if not ai_response:
            raise ValueError("AI returned an empty response.")


        print("\nAI RESPONSE:")
        print(ai_response)


        # ====================================================
        # PARSE JSON
        # ====================================================

        try:

            result = json.loads(ai_response)

        except json.JSONDecodeError as json_error:

            print("\nJSON PARSE ERROR:")
            print(str(json_error))

            raise ValueError(
                "AI returned an invalid JSON response."
            )


        # ====================================================
        # EXTRACT TASKS
        # ====================================================

        tasks = result.get("tasks")


        if not isinstance(tasks, list):
            raise ValueError(
                "AI response does not contain a valid task list."
            )


        # ====================================================
        # CLEAN TASKS
        # ====================================================

        cleaned_tasks = []

        for task in tasks:

            if isinstance(task, str):

                task = task.strip()

                if task:
                    cleaned_tasks.append(task)


        # ====================================================
        # VALIDATE TASK COUNT
        # ====================================================

        if not cleaned_tasks:

            raise ValueError(
                "AI generated no usable tasks."
            )


        # Keep the application controlled even if AI returns
        # more tasks than requested.

        cleaned_tasks = cleaned_tasks[:10]


        print("\nGENERATED TASKS:")

        for index, task in enumerate(cleaned_tasks, start=1):
            print(f"{index}. {task}")


        # ====================================================
        # SEND RESPONSE TO FRONTEND
        # ====================================================

        return jsonify({

            "success": True,

            "tasks": cleaned_tasks,

            "count": len(cleaned_tasks)

        })


    # ========================================================
    # OPENAI / GROQ API ERRORS
    # ========================================================

    except Exception as error:

        print("\n========================================")
        print("AI GENERATION ERROR")
        print("========================================")
        print(type(error).__name__)
        print(str(error))


        return jsonify({

            "success": False,

            "error": str(error)

        }), 500


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=True
    )
    