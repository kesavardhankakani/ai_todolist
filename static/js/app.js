const goalInput = document.getElementById("goal");
const deadlineInput = document.getElementById("deadline");
const priorityInput = document.getElementById("priority");

const generateBtn = document.getElementById("generateBtn");
const generateText = document.getElementById("generateText");
const generateIcon = document.getElementById("generateIcon");

const errorMessage = document.getElementById("errorMessage");
const errorText = document.getElementById("errorText");

const loadingSection = document.getElementById("loadingSection");
const resultsSection = document.getElementById("resultsSection");

const resultGoal = document.getElementById("resultGoal");
const taskList = document.getElementById("taskList");

const regenerateBtn = document.getElementById("regenerateBtn");
const newPlanBtn = document.getElementById("newPlanBtn");

const goalCounter = document.getElementById("goalCounter");

const progressText = document.getElementById("progressText");
const progressPercentage = document.getElementById("progressPercentage");
const progressBar = document.getElementById("progressBar");

let currentTasks = [];


/* ========================================
   INITIAL SETUP
======================================== */

document.addEventListener("DOMContentLoaded", () => {

    setMinimumDeadline();

    updateGoalCounter();

});


/* ========================================
   DEADLINE
======================================== */

function setMinimumDeadline() {

    if (!deadlineInput) {
        return;
    }

    const today = new Date();

    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, "0");
    const day = String(today.getDate()).padStart(2, "0");

    deadlineInput.min = `${year}-${month}-${day}`;
}


/* ========================================
   GOAL COUNTER
======================================== */

goalInput.addEventListener("input", updateGoalCounter);

function updateGoalCounter() {

    if (!goalInput || !goalCounter) {
        return;
    }

    goalCounter.textContent =
        `${goalInput.value.length} / 500`;
}


/* ========================================
   ERROR HANDLING
======================================== */

function showError(message) {

    if (!errorMessage || !errorText) {
        return;
    }

    errorText.textContent =
        message || "Something went wrong. Please try again.";

    errorMessage.classList.remove("hidden");

    errorMessage.scrollIntoView({
        behavior: "smooth",
        block: "center"
    });
}


function hideError() {

    if (!errorMessage) {
        return;
    }

    errorMessage.classList.add("hidden");
}


/* ========================================
   LOADING STATE
======================================== */

function setLoading(isLoading) {

    if (isLoading) {

        generateBtn.disabled = true;

        generateIcon.textContent = "⏳";
        generateText.textContent = "Creating Your Plan...";

        loadingSection.classList.remove("hidden");

        resultsSection.classList.add("hidden");

    } else {

        generateBtn.disabled = false;

        generateIcon.textContent = "✨";
        generateText.textContent = "Generate My Plan";

        loadingSection.classList.add("hidden");
    }
}


/* ========================================
   FORM VALIDATION
======================================== */

function validateForm() {

    const goal = goalInput.value.trim();
    const deadline = deadlineInput.value;
    const priority = priorityInput.value;

    if (!goal) {
        showError("Please enter a goal.");
        goalInput.focus();
        return false;
    }

    if (goal.length < 3) {
        showError("Please enter a more detailed goal.");
        goalInput.focus();
        return false;
    }

    if (!deadline) {
        showError("Please select a deadline.");
        deadlineInput.focus();
        return false;
    }

    if (!priority) {
        showError("Please select a priority.");
        priorityInput.focus();
        return false;
    }

    return true;
}


/* ========================================
   GENERATE PLAN
======================================== */

async function generatePlan() {

    hideError();

    if (!validateForm()) {
        return;
    }

    const goal = goalInput.value.trim();
    const deadline = deadlineInput.value;
    const priority = priorityInput.value;

    setLoading(true);

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


        let data;

        try {
            data = await response.json();
        } catch (jsonError) {

            throw new Error(
                `Server returned an invalid response (${response.status}).`
            );
        }


        if (!response.ok || !data.success) {

            throw new Error(
                data.error ||
                `Failed to generate plan (${response.status}).`
            );
        }


        if (
            !Array.isArray(data.tasks) ||
            data.tasks.length === 0
        ) {
            throw new Error(
                "The AI did not generate any usable tasks."
            );
        }


        currentTasks = data.tasks;

        displayResults(
            goal,
            currentTasks
        );


    } catch (error) {

        console.error("Plan generation error:", error);

        showError(
            error.message ||
            "Unable to generate your plan. Please try again."
        );

    } finally {

        setLoading(false);
    }
}


/* ========================================
   DISPLAY RESULTS
======================================== */

function displayResults(goal, tasks) {

    resultsSection.classList.remove("hidden");

    resultGoal.textContent =
        `"${goal}"`;

    renderTasks(tasks);

    updateProgress();

    setTimeout(() => {

        resultsSection.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });

    }, 100);
}


/* ========================================
   RENDER TASKS
======================================== */

function renderTasks(tasks) {

    taskList.innerHTML = "";

    tasks.forEach((task, index) => {

        const taskItem = document.createElement("div");

        taskItem.className = "task-item";

        const checkbox =
            document.createElement("input");

        checkbox.type = "checkbox";

        checkbox.className = "task-checkbox";

        checkbox.dataset.index = index;


        const taskText =
            document.createElement("div");

        taskText.className = "task-text";

        taskText.textContent = task;


        checkbox.addEventListener(
            "change",
            () => {

                if (checkbox.checked) {

                    taskItem.classList.add("completed");

                } else {

                    taskItem.classList.remove("completed");
                }

                updateProgress();
            }
        );


        taskItem.appendChild(checkbox);
        taskItem.appendChild(taskText);

        taskList.appendChild(taskItem);
    });
}


/* ========================================
   PROGRESS
======================================== */

function updateProgress() {

    const checkboxes =
        document.querySelectorAll(".task-checkbox");

    const total = checkboxes.length;

    const completed =
        document.querySelectorAll(
            ".task-checkbox:checked"
        ).length;


    if (total === 0) {

        progressText.textContent =
            "0 / 0 completed";

        progressPercentage.textContent =
            "0%";

        progressBar.style.width =
            "0%";

        return;
    }


    const percentage =
        Math.round((completed / total) * 100);


    progressText.textContent =
        `${completed} / ${total} completed`;

    progressPercentage.textContent =
        `${percentage}%`;

    progressBar.style.width =
        `${percentage}%`;
}


/* ========================================
   GENERATE BUTTON
======================================== */

generateBtn.addEventListener(
    "click",
    generatePlan
);


/* ========================================
   REGENERATE
======================================== */

regenerateBtn.addEventListener(
    "click",
    async () => {

        hideError();

        await generatePlan();
    }
);


/* ========================================
   NEW PLAN
======================================== */

newPlanBtn.addEventListener(
    "click",
    () => {

        currentTasks = [];

        resultsSection.classList.add("hidden");

        goalInput.value = "";

        deadlineInput.value = "";

        priorityInput.value = "";

        updateGoalCounter();

        hideError();

        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });

        setTimeout(() => {
            goalInput.focus();
        }, 400);
    }
);


/* ========================================
   ENTER KEY SUPPORT
======================================== */

goalInput.addEventListener(
    "keydown",
    (event) => {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {
            event.preventDefault();

            generatePlan();
        }
    }
);
