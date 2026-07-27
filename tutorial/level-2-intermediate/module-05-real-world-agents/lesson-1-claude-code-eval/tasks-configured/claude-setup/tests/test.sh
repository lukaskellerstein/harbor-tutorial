#!/bin/bash
# One assertion per Claude Code configuration surface. The reward is the
# fraction that passed, so a partial score tells you exactly WHICH surface
# failed to load -- the whole point of this task. A plain pass/fail would
# just say "something broke".
#
# Silent failure is the normal failure mode here: if a surface does not load,
# Claude Code does not error, it simply behaves as if the file were not there.

REPORT=/app/report.md
PASSED=0
TOTAL=5

pass() {
  echo "PASS: $1"
  PASSED=$((PASSED + 1))
}

fail() {
  echo "FAIL: $1"
}

echo "--- /app/report.md ---"
cat "$REPORT" 2>/dev/null || echo "(missing)"
echo "----------------------"

# 1. Skill: only .claude/skills/harbor-report/SKILL.md specifies this layout.
if [ "$(sed -n '1p' "$REPORT" 2>/dev/null)" = "# Build Report" ] \
   && grep -qx 'Verified-By: fact-checker' "$REPORT" 2>/dev/null; then
  pass "skill loaded (report follows the harbor-report format)"
else
  fail "skill did not load (report header/Verified-By line missing)"
fi

# 2. MCP server: the build code exists only inside the stdio server, so the
#    agent cannot produce it without actually connecting and calling the tool.
if grep -qx 'Build-Code: HRB-7391' "$REPORT" 2>/dev/null; then
  pass "MCP server loaded (build code came from get_build_code)"
else
  fail "MCP server did not load (build code absent or wrong)"
fi

# 3. CLAUDE.md: it alone requires this trailer as the final line.
if [ "$(tail -n 1 "$REPORT" 2>/dev/null)" = "Generated-By: harbor-tutorial" ]; then
  pass "CLAUDE.md loaded (trailer line present)"
else
  fail "CLAUDE.md did not load (trailer line missing)"
fi

# 4. Subagent: Claude Code writes a delegated turn to its own subagents/ JSONL.
#    Look in both places -- the live config dir, and the copy the Stop hook
#    makes into the mounted log dir.
if find /app/.claude/projects /logs/agent/sessions/projects \
     -path '*subagents*' -name '*.jsonl' 2>/dev/null | grep -q .; then
  pass "subagent loaded (fact-checker ran in its own context)"
else
  fail "subagent did not load (no subagents/*.jsonl transcript)"
fi

# 5. Hooks: the PostToolUse hook appends every Write/Edit payload here.
if [ -s /logs/agent/hook-events.jsonl ]; then
  pass "hooks loaded (PostToolUse hook fired on Write/Edit)"
else
  fail "hooks did not load (/logs/agent/hook-events.jsonl empty or missing)"
fi

echo "Score: $PASSED/$TOTAL"
python3 -c "print($PASSED / $TOTAL)" > /logs/verifier/reward.txt
