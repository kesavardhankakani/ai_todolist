from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
import os
import json

# Load .env file
load_dotenv()

# Create Flask application
app = Flask(__name__)

# Get Groq API key
api_key = os.getenv("GROQ_API_KEY")

# Check API key
print("API KEY FOUND:", bool(api_key))

# Create Groq client
client = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1"
)

# ==================================================
# HOME PAGE
# ==================================================

@app.route("/")
def home():

    return render_template("index.html")


# ==================================================
# AI TO-DO GENERATOR
# ==================================================

@app.route("/generate", methods=["POST"])
def generate():

    try:

        # Get data from JavaScript
        data = request.get_json()

        goal = data.get("goal")
        deadline = data.get("deadline")
        priority = data.get("priority")


        # ------------------------------------------
        # Validate input
        # ------------------------------------------

        if not goal:

            return jsonify({
                "error": "Goal is required"
            }), 400


        if not deadline:

            return jsonify({
                "error": "Deadline is required"
            }), 400


        if not priority:

            return jsonify({
                "error": "Priority is required"
            }), 400


        print("\n================================")
        print("AI TO-DO REQUEST")
        print("================================")

        print("Goal:", goal)
        print("Deadline:", deadline)
        print("Priority:", priority)


        # ------------------------------------------
        # Prompt for AI
        # ------------------------------------------

        prompt = f"""
You are an expert AI productivity assistant.

Create a personalized and realistic to-do list.

USER GOAL:
{goal}

DEADLINE:
{deadline}

PRIORITY:
{priority}

REQUIREMENTS:

1. Generate 8 to 10 tasks.
2. Every task must directly help achieve the user's goal.
3. Do NOT generate generic tasks.
4. Do NOT say things like "start working on your goal".
5. Tasks must be specific and actionable.
6. Arrange tasks in a logical order.
7. Consider the deadline.
8. Consider the priority level.
9. Make the tasks realistic for a normal person.
10. Each task should be short and clear.
11. Return ONLY a JSON array.
12. Do not use Markdown.
13. Do not add explanations.

Example:

[
    "Research the fundamentals of the topic",
    "Create a realistic daily schedule",
    "Practice the first major skill",
    "Complete a small practical project"
]
"""


        # ------------------------------------------
        # Call Groq AI
        # ------------------------------------------

        response = client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert AI productivity "
                        "and task planning assistant."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.7,

            response_format={
                "type": "json_object"
            }

        )


        # ------------------------------------------
        # Get AI response
        # ------------------------------------------

        ai_response = response.choices[0].message.content

        print("\nAI RESPONSE:")
        print(ai_response)


        # ------------------------------------------
        # Convert response to Python
        # ------------------------------------------

        result = json.loads(ai_response)


        # ------------------------------------------
        # Get tasks
        # ------------------------------------------

        if isinstance(result, dict) and "tasks" in result:

            tasks = result["tasks"]

        elif isinstance(result, list):

            tasks = result

        else:

            raise ValueError(
                "AI returned an invalid task format"
            )


        # ------------------------------------------
        # Validate tasks
        # ------------------------------------------

        if not isinstance(tasks, list):

            raise ValueError(
                "Tasks are not in list format"
            )


        if len(tasks) == 0:

            raise ValueError(
                "AI returned no tasks"
            )


        print("\nGenerated tasks:")

        for task in tasks:
            print("-", task)


        # ------------------------------------------
        # Send tasks to JavaScript
        # ------------------------------------------

        return jsonify({
            "tasks": tasks
        })


    except Exception as e:

        print("\n================================")
        print("ERROR")
        print("================================")

        print(str(e))


        return jsonify({
            "error": str(e)
        }), 500


# ==================================================
# START FLASK
# ==================================================

if __name__ == "__main__":

    app.run(debug=True)