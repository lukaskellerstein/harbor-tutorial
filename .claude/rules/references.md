---
globs: ["tutorial/**"]
---

# Reference Sources

Always consult these sources when building lessons. Do NOT guess at APIs — read the source code first.

## Harbor
- **Source code**: /Users/lkellers/Projects/github/harbor-framework/harbor
- **GitHub**: https://github.com/harbor-framework/harbor
- **Docs**: https://harborframework.com/docs
- **Cookbook**: https://github.com/harbor-framework/harbor-cookbook

## LMStudio (local model serving)
- **CLI docs**: https://lmstudio.ai/docs/cli
- **Headless mode**: https://lmstudio.ai/docs/developer/core/headless
- **Selected model**: Gemma4-E4B — https://lmstudio.ai/models/google/gemma-4-e4b

## AI Agent Frameworks
| Framework | Source Code | Examples |
|-----------|------------|----------|
| Langchain | /Users/lkellers/Projects/github/langchain-ai/langchain | /Users/lkellers/Projects/github/lukaskellerstein/ai-agents-course/Version_2/6_langchain-ai/1_langchain |
| Langgraph | /Users/lkellers/Projects/github/langchain-ai/langgraph | /Users/lkellers/Projects/github/lukaskellerstein/ai-agents-course/Version_2/6_langchain-ai/2_langgraph |
| Deepagents | /Users/lkellers/Projects/github/langchain-ai/deepagents | /Users/lkellers/Projects/github/lukaskellerstein/ai-agents-course/Version_2/6_langchain-ai/3_deepagents |
| Claude Agent SDK | /Users/lkellers/Projects/github/anthropics/claude-agent-sdk-python | /Users/lkellers/Projects/github/lukaskellerstein/vibe-coding-course/5_Claude_Agent_SDK/python |

## RAG
- **Vector DB**: Qdrant — https://qdrant.tech/

## Evaluation Benchmarks
- **SWE-Bench**: https://huggingface.co/datasets/SWE-bench/SWE-bench_Verified
- **Terminal-Bench**: https://www.tbench.ai

## How to Use References

1. Before using a Harbor API or CLI command, check the source code at the path above.
2. Before referencing an agent framework, check its source code and examples.
3. When a lesson needs a local model, use LMStudio with the Gemma4-E4B model.
