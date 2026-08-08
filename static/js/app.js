console.log("Script Loaded");

const generateBtn = document.getElementById("generateBtn");
const goalInput = document.getElementById("goal");
const deadlineInput = document.getElementById("deadline");
const priorityInput = document.getElementById("priority");
const taskList = document.getElementById("taskList");


generateBtn.addEventListener("click", async function () {

    const goal = goalInput.value.trim();
    const deadline = deadlineInput.value;
    const priority = priorityInput.value;


    if (!goal) {
        alert("Please enter your goal.");
        return;
    }

    if (!deadline) {
        alert("Please select a deadline.");
        return;
    }

    if (!priority) {
        alert("Please select a priority.");
        return;
    }


    generateBtn.disabled = true;
    generateBtn.textContent = "Generating...";

    taskList.innerHTML = "<li>Generating tasks...</li>";


    try {

        const response = await fetch("/generate", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                goal: goal,
                deadline: deadline,
                priority: priority
            })

        });


        console.log("Response status:", response.status);


        if (!response.ok) {

            const errorText = await response.text();

            console.error("Server error:", errorText);

            throw new Error(
                "Server returned " + response.status
            );
        }


        const data = await response.json();

        console.log("Received data:", data);


        taskList.innerHTML = "";


        if (data.tasks && data.tasks.length > 0) {

            data.tasks.forEach(function (task, index) {

                const li = document.createElement("li");

                li.innerHTML = `
                    <strong>Task ${index + 1}</strong>
                    <p>${task}</p>
                `;

                taskList.appendChild(li);

            });

        } else {

            taskList.innerHTML = `
                <li>No tasks generated.</li>
            `;

        }

    }

    catch (error) {

        console.error("Generation error:", error);

        taskList.innerHTML = `
            <li class="error">
                Failed to generate tasks.
                Please try again.
            </li>
        `;

    }

    finally {

        generateBtn.disabled = false;

        generateBtn.textContent = "Generate To-Do List";

    }

});