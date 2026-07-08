# Which Practice Challenged Me Most — Reflection

**Credit Risk Intelligence Platform | 30-Day Leadership Development Program — Capstone**
**Authors:** Akash Chaurasiya, Ashu Sharma

---

## 1. Which practice was hardest to sustain, and why?

If I had to pick one, it would be **acceptance and adaptability**. Building the Credit Risk Intelligence Platform, we ran into a string of problems that had nothing to do with our own code logic and everything to do with the environment around us. LLM providers kept letting us down in different ways — Gemini deprecations, OpenAI throwing 401 errors, Groq rate limits — and each time, there was nothing we could do to prevent it upstream, only respond. Then we hit an Azure CI/CD wall when it turned out we didn't have Owner role for our service principal, which meant the deployment approach we'd already built had to be scrapped for something else. And on top of that, a SyntaxError showed up only inside Docker's Python 3.11 environment — completely invisible on our local machines, so it looked like everything worked until it didn't.

None of these were one-time fixes. Each one meant we had to stop treating the problem as a bug to squash and start treating it as a constraint to design around — which is really what adaptability comes down to. We ended up building a three-provider fallback chain instead of trusting any single LLM to stay stable, and we started testing inside Docker before every deploy instead of trusting local runs. What made this hard to sustain wasn't any single incident — it was that the lesson kept repeating in a new shape every time, so there was no point where it started feeling easy.

## 2. Where did a peer support me in a way I didn't expect?

Working as a two-person team, support looked less like encouragement and more like shared debugging load. The clearest example was our hallucination problem — our DeepEval score started at 0.58, which wasn't good enough. Neither of us solved that alone. It was only through going back and forth, questioning each other's assumptions about why the retrieval was failing, that we landed on hybrid BM25 plus vector search with year-aware re-ranking, which brought the score down to 0.22. That fix didn't come from one person's insight — it came from the disagreement itself.

Splitting ownership also mattered more than I expected going in. One of us focused on the RAG pipeline and retrieval quality, the other on infrastructure and Azure deployment. When one side hit a wall — like the Azure permissions issue — the other could keep moving on their half instead of the whole project stalling out. And honestly, the biggest unexpected support was just having someone to explain a bug to out loud. More than once, I found the fix mid-sentence, before my teammate had even finished responding — just from being forced to articulate the problem clearly to another person.

## 3. What's one practice I want to intentionally strengthen going forward?

I want to get better at **reflective practice** — specifically, doing it *during* a project instead of only at the end. Looking back at our own "what we'd do differently" list — using managed auth from day one, pinning dependency versions early, setting up LangSmith tracing from the start, adding a job queue for large PDFs — every one of those is a lesson that only surfaced because we stopped to reflect once the project was basically done. Going forward, I want to build in short after-action reviews after each major milestone, not just at the finish line, so lessons like "pin your versions" get applied to the next sprint instead of only carrying forward into the next project.

---

*Prepared for the Values-Based Leadership Capstone discussion (Slide 14), using real challenges from the Credit Risk Intelligence Platform project as the basis for reflection.*
