# Day 01 | Getting Started with Agentic AI 🚀

## What was Day 1 about?

Day 1 was my introduction to **Agentic AI**.

The main goal was to understand what actually goes into building an AI agent instead of just sending a prompt to an AI model and getting a response.

I started by setting up the environment and then worked through the provided hands-on lab.

---

## 🛠️ Setting Up

I worked on the setup locally on my MacBook.

The setup included:

* Python
* A Python virtual environment
* Required Python packages
* Gemini API
* `.env` file for storing the API key
* Git and GitHub

I generated my Gemini API key and connected it to the project through the `.env` file.

---

## 🧠 Things I Learned

### Model Calls

I learned how a Python application can communicate with an AI model through an API.

One thing that stood out to me was that the model doesn't automatically remember everything from previous messages. The application has to provide the required conversation history.

### Tools

Then I got introduced to **tools**.

The basic idea was interesting: the AI model can decide that it needs a tool, but the actual application is responsible for running that tool and sending the result back.

So the model doesn't magically execute everything by itself.

### Agent Loop

This helped me understand what makes an agent different from a simple AI call.

The basic flow I understood was:

**User → Model → Tool (if needed) → Tool Result → Model → Final Response**

The model can take an action, observe the result, and continue from there.

### Memory

I also learned about how conversation context can be maintained by the application and passed back to the model when needed.

This made the idea of "memory" in AI applications much clearer to me.

### Handling Errors

Another part I explored was **self-healing**.

Instead of an error simply ending the process, the error information can become part of what the agent observes, allowing it to try to recover.

---

## 💻 My Day 1 Experience

The setup wasn't completely smooth.

When I ran the setup, I faced a `NotFoundError` with the `gemini-2.5-flash` model.

I tried changing the model configuration to `gemini-2.5-flash-lite`, but I still faced the same issue.

I then tried checking the available models, where I ran into a missing `dotenv` module.

So Day 1 wasn't just about learning the concepts. I also got my first experience of troubleshooting an AI project when things didn't work as expected.

---

## 🔍 What Finally Clicked

Before this, I mostly thought about AI in terms of:

**Prompt → Response**

Day 1 made me look at it differently:

**User → Agent → Model → Tools / Context → Model → Response**

The model is only one part of the system. The application around it is what allows the agent to interact with tools, maintain context, and handle what happens during execution.

That was probably my biggest takeaway from Day 1.

---

## 🧰 Technologies I Used

* Python
* Gemini API
* OpenAI-compatible Python client
* Git
* GitHub
* Python virtual environment

---

## 📌 Day 1 Takeaway

Day 1 gave me my first hands-on look at how agentic AI systems are structured.

I started with the setup, generated my API key, worked through the lab, learned about model calls, tools, agent loops, memory and error handling, and also had to troubleshoot a model/API issue along the way.

**One day in, and I'm already seeing AI as more than just a prompt box. 🚀**
