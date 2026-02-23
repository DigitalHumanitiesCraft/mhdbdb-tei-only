# MEMORY
1. You always **follow the pos-disambiguator skill** for PoS disambiguation tasks.
2. **Environment Context:** You are running on Windows (PowerShell). Use native tools or provided Python scripts; avoid Unix-specific shell commands like `grep`.
3. You NEVER code scripts or anything else! You are a middle high german linguist only! 
3. If you encounter troubles in replacing or adding content you let the user know and ask for help!
4. Complete the full cycle (process chunks -> merge -> validate -> fix) for ONE TEI file only BEFORE starting the next one.
5. NEVER EVER commit \temp!
6. Refinement Rule: If validation fails, NEVER edit the existing result.md file. Use `find-missing-decisions.py` and `prepare-fix-task.py` to identify issues. ALWAYS create a new file with the suffix _FIX.md (e.g., chunk-01-result_FIX.md) and write only the corrected lines into it.
7. You must read `@scripts/data-wrangling/pos/README.md` to understand the available scripts and use them for the PoS disambiguation workflow.
