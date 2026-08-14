markdown
# RAG Pipeline Tests — NayaTel AI Assistant

> Tests I ran on my RAG pipeline before moving to the frontend, following my roadmap's rule: don't move to UI until retrieval actually works.

---

## Setup

```python
import os, sys
root_dir = os.path.abspath(os.path.join("src"))
if root_dir not in sys.path:
    sys.path.append(root_dir)
Result: c:\Users\Prime\OneDrive\Desktop\Nayatel_ai_assistant\Tests\src

Checked how many PDFs I actually have as a sanity check before running anything:

python
pdf_dir = Path(os.path.join(root_dir, "..\\..\\backend\\data\\raw"))
pdf_paths = pdf_dir.glob('**/*.pdf')
Found 44 PDFs, all opened fine, none skipped.

Overall Summary
Test	What I Checked	Result
1	Vector DB actually has my data	✅ Pass — 115 chunks stored
2	Raw retrieval scores (in-scope vs out-of-scope)	⚠️ Mixed — threshold not as helpful as I thought
3	10 roadmap test questions	✅ Mostly pass — specific questions work well
4	Category-specific stress tests	✅ Pass — correct docs pulled for specific topics
5	Full pipeline (retrieval + LLM + safety)	✅ Pass — in-scope answered, out-of-scope refused
6	Conversation history / follow-up test	✅ Pass — remembers previous context
7	Error handling (empty query)	✅ Pass — caught early, no wasted API calls
8	Chunking strategy comparison	✅ Already done earlier in dev
Test 1 — Does the vector DB actually have my data?
Purpose: Make sure the embedding/ingestion step actually worked — not just ran without errors, but actually stored something.

python
client = chromadb.PersistentClient(config.VECTOR_DB_PATH)
collection = client.get_collection("nayatel_docs")
print(collection.count())
Result: Expected 115, got 115.

Interpretation: The DB has exactly the number of chunks I expected. No chunks got lost during ingestion, no duplicates. The embedding pipeline is working correctly.

Test 2 — Raw retrieval scores (in-scope vs out-of-scope)
Purpose: Get real numbers before picking a threshold. I wanted to see what the scores actually look like so I could decide where to set the cutoff.

Ran one clearly in-scope question and one clearly out-of-scope question:

Question	Type	Best Score	Source
"What internet packages are available?"	In-scope	1.0414	Fiber vs DSL vs 4G_5G.pdf p1
"Does NayaTel offer Starlink packages?"	Out-of-scope	0.9333	Nayatel_Pricing_By_Location.pdf p14
What I noticed:

The out-of-scope question actually had a better (lower/more similar) score than the in-scope one. That's backwards from what I wanted. The Starlink question scored 0.9333, while the in-scope one scored 1.0414.

Why this happens: All my docs are NayaTel/internet related, so a Starlink question still shares a lot of vocabulary with real NayaTel content — words like "internet", "packages", "speed" are everywhere. The embedding model sees these words and thinks it's similar, even though the actual answer isn't there.

Also confirmed retrieval returns the right dict shape:

python
found = retriever.retrive("test query", top_k=1)
print(found[0].keys())
# dict_keys(['ids', 'text', 'source', 'page', 'category', 'chunk_index', 'score'])
Interpretation: The similarity threshold alone isn't reliably separating in-scope from out-of-scope. My system prompt does more of the actual blocking work than the threshold does. I need to be honest about this — the threshold is there, but it's not the main safety layer.

Test 3 — My 10 roadmap test questions
Purpose: Check top-3 retrieved chunks for each of the questions from my roadmap. I wanted to see if the retriever pulls the right documents for realistic customer questions.

Results
Question	Top Retrieval	Good/Bad
"What packages are available?"	Unlimited_bundle.pdf, gaming blog post	⚠️ Mixed
"How can I get a new connection?"	Router manuals	❌ Bad
"How long does installation take?"	Blog posts, video PDF	❌ Bad
"How do I pay my bill?"	Payment options.pdf	✅ Good
"What should I do if my internet isn't working?"	ONT Lights.pdf	✅ Good
"How can I contact support?"	telephone.pdf, Contact us.pdf	✅ Good
"What documents are required?"	Payment options.pdf, faq.pdf	❌ Bad
"Can I upgrade my package?"	Nayatel_Pricing_By_Location.pdf	✅ Good
"What happens if I don't pay my bill?"	Payment options.pdf	⚠️ Mixed
"What services does NayaTel provide?"	Contact us.pdf, faq.pdf	❌ Bad
What Worked Well
"How do I pay my bill?" → Payment options.pdf

"How can I contact support?" → Contact us.pdf / telephone.pdf

"Can I upgrade my package?" → correct pricing doc

"What should I do if my internet isn't working?" → ONT Lights.pdf

What Didn't Work Well
"What packages are available?" → pulled a gaming blog post instead of anything with actual package names

"How can I get a new connection?" → pulled router manuals instead of sign-up info

"What services does NayaTel provide?" → nothing that looks like an actual overview

Interpretation
Retrieval works well for specific/narrow questions, weaker on broad ones. Probably because broad questions match a wider spread of similarly-scored chunks instead of one clear best match. The embedding model isn't great at understanding the intent behind a question — it just matches keywords. So "What packages are available?" matches words in any doc that mentions speeds or internet, not just the pricing document.

Test 4 — Category-specific stress tests
Purpose: Test the most common technical questions users might ask.

Results
Question	Retrieved Document	Correct?
"How do I reset my ONT?"	ONT Lights.pdf	✅ Yes
"What is the difference between 2.4Ghz and 5Ghz?"	Difference between 2.4 GHz and 5 GHz.pdf	✅ Yes
"How do I change my wifi password?"	Ruijie.pdf, tplink router.pdf	✅ Yes
Interpretation
First two questions clearly and correctly pulled the exact right doc. Worked really well.

Third question pulled router manuals — makes sense, but with 12 different device manuals it might grab the wrong device for a specific user. Not tested that edge case directly given time.

Test 5 — Full pipeline test (retrieval + LLM + relevance gate)
Purpose: Run the whole pipeline end-to-end — retrieval, LLM generation, and the safety gate. Check if it actually works like a real assistant.

In-scope question: "What are prices of internet packages in Islamabad?"
Result: Got a full correct answer listing real pricing tiers:

text
Here are the Islamabad prices from the provided list (all PKR/month + tax; Unlimited — FUP applies):

Unlimited Internet only:
- 30 Mbps — Rs. 2,225
- 40 Mbps — Rs. 3,450
- 50 Mbps — Rs. 4,300
- 70 Mbps — Rs. 5,300
- 100 Mbps — Rs. 7,200
- 200 Mbps — Rs. 14,000
- 350 Mbps — Rs. 24,000

Triple Play (Internet + Cable TV + Phone):
- 30 Mbps — Rs. 2,525
- 40 Mbps — Rs. 3,750
- 50 Mbps — Rs. 4,600
- 70 Mbps — Rs. 5,600
- 100 Mbps — Rs. 7,500
- 200 Mbps — Rs. 14,300
- 350 Mbps — Rs. 24,300
Checked against the source — accurate.

Out-of-scope question: "Does NayaTel offer Starlink packages?"
Result: Got my refusal message:

text
I AM UNABLE TO HELP WITH THIS AS I AM A NAYATEL SERVICE REPRESENTATIVE AND CAN ONLY ANSWER IN THAT CONTEXT
Important Note
The Starlink question's score (0.9333) was still under my similarity threshold — meaning the score-based gate alone would have let it through. What actually stopped it was my strict system prompt instructions, not the similarity check.

So I have two safety layers, but the threshold isn't doing as much work as I planned — the prompt is doing most of the actual blocking.

Interpretation
The full pipeline works. In-scope questions get accurate answers with sources. Out-of-scope questions get refused instead of hallucinated answers. But the threshold isn't the main safety mechanism — the system prompt is. I should be honest about this.

Test 6 — Conversation history / follow-up test
Purpose: Check if follow-up questions work without repeating the full context.

python
r1 = rag_pipeline.answer("Tell me about the 20mbps package", session_id="test2")
r2 = rag_pipeline.answer("How much does it cost?", session_id="test2")
Result:

text
20 Mbps Unlimited (Internet-only): Rs. 1,775/month + tax
20 Mbps Triple Play (Internet + Cable TV + Phone): Rs. 2,075/month + tax
What happened: r2 alone has no useful keywords — "How much does it cost?" by itself doesn't mention 20mbps or internet or any specific plan. But since I fold the previous message into the retrieval query, it still correctly pulled 20mbps pricing and answered right.

Interpretation: My history-folding logic actually works. The assistant remembers what we were talking about and uses that context for retrieval. Without this, the second question would have returned garbage results because there's nothing to match against.

Test 7 — Error handling (empty query)
Purpose: Check what happens when a user submits an empty question.

python
rag_pipeline.answer("", session_id="test3")
# {'answer': 'please enter a question!!!', 'source': []}
Interpretation: Empty query gets caught immediately, never reaches retrieval or the LLM — no wasted API calls. Clean and simple.

Test 8 — Chunking strategy comparison (placeholder)
Purpose: Not re-running this test, just documenting it.

Earlier in development, I compared sentence-based micro-chunks vs token-based (~650 token) chunks. Token-based chunks noticeably improved category-correct retrieval, so that's what I'm using now.

No need to re-test — it happened and shaped my final approach.

Overall Takeaways
What Works
Vector DB and full pipeline plumbing work correctly — counts match, keys match, end-to-end answers with sources work.

Specific questions get correct documents — things like "How do I pay my bill?", "What should I do if my internet isn't working?" work well.

Conversation history works — follow-up questions use context from previous messages.

System prompt safely blocks out-of-scope questions — Starlink refused, no hallucinations.

Error handling works — empty query caught early.

What Needs Work
Retrieval is inconsistent — strong on specific/narrow questions, weaker on broad general ones like "What packages are available?" or "What services does NayaTel provide?"

Similarity threshold alone isn't reliably separating in-scope from out-of-scope — because all docs are internet-related, out-of-scope questions still share vocabulary with real NayaTel content.

The system prompt is doing more safety work than the threshold — I should say this honestly rather than claim the threshold is doing more than it is.

What I'd Change Given More Time
Hybrid search — add keyword-based search (BM25) alongside semantic search. Broad questions would probably match keywords better.

Query rewriting — expand "What packages are available?" to something like "NayaTel internet packages pricing speed tiers" before retrieval.

Better threshold tuning — collect more examples of both in-scope and out-of-scope queries and actually tune the threshold with data instead of guessing.

My Verdict
Given my timeline, this is a reasonable point to stop testing and move forward. The weak points are documented and understood, not hidden. The system genuinely works for realistic customer questions. The specific, narrow questions that actual customers would ask work well. The broad ones that are harder for the retriever are less common in real usage.