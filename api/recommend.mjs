// Vercel Function: POST /api/recommend
// 열쇠(GEMINI_API_KEY)는 서버의 환경 변수에서만 읽는다. 화면(index.html)에는 열쇠가 가지 않는다.
// 후보는 화면이 보낸 목록을 믿지 않고, 조건 두 개만 받아 data/data.json 에서 다시 고른다.
import { readFile } from "node:fs/promises";
import path from "node:path";

// 모델 이름: https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash-lite
// 부르는 방법: https://ai.google.dev/gemini-api/docs/text-generation (Interactions API)
const MODEL = "gemini-3.5-flash-lite";
const ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/interactions";
const API_REVISION = "2026-05-20";
const MAX_CANDIDATES = 5;

const SYSTEM_INSTRUCTION = [
  "너는 초등 수학 문제집 비교 도우미다. 사용자가 준 후보 표 안에서만 한 권을 고른다.",
  "규칙:",
  "1. name 에는 후보 표의 name 하나를 글자 하나 바꾸지 말고 그대로 쓴다.",
  "2. reasons 는 정확히 두 줄이다. 첫 줄에는 추천한 책의 price 를, 둘째 줄에는 추천한 책의 sales_point 를 후보 표의 값 그대로 반드시 넣는다.",
  "3. reasons 에 쓰는 숫자는 추천한 책의 price 와 sales_point 두 값뿐이다. 예산 · 학년-학기 · 책 이름 속 숫자 · 다른 후보의 숫자는 쓰지 않는다.",
  "4. 다른 후보와 견줄 때는 후보 표로 사실인 것만 숫자 없이 말로 쓴다.",
  "5. 후보 표에 없는 책이나 표에 없는 정보(난이도 · 후기 · 저자 · 학습 효과 등)는 말하지 않는다.",
  "6. sales_point 는 \"세일즈포인트\" 라고만 부른다. \"인기\" 나 \"판매량\" 같은 말로 바꿔 말하지 않는다.",
  "7. reasons 의 각 줄은 띄어쓰기를 포함해 40자 안쪽으로 쓴다.",
  "8. \"합리적\" · \"알맞다\" · \"부담이 적다\" · \"많은 선택\" · \"인기\" 처럼 후보 표에 없는 판단이나 평가는 쓰지 않는다.",
].join("\n");

// ---- 조건 계산 (index.html 과 같은 방식) ----
const isMath = (item) => item.name.includes("수학");
const termRe = (t) => new RegExp("(?<![0-9])" + t + "(?![0-9])");

function match(items, budget, term) {
  const re = term ? termRe(term) : null;
  return items.filter((item) =>
    isMath(item) &&
    (budget === null || item.price <= budget) &&
    (!re || re.test(item.name)));
}

// price 낮은 순, 같으면 data.json 순서 (Array.sort 는 안정 정렬)
const candidatesFor = (items, budget, term) =>
  [...match(items, budget, term)].sort((a, b) => a.price - b.price).slice(0, MAX_CANDIDATES);
// ---- 조건 계산 끝 ----

let itemsCache = null;
async function loadItems() {
  if (!itemsCache) {
    const file = path.join(process.cwd(), "data", "data.json");
    itemsCache = JSON.parse(await readFile(file, "utf8"));
  }
  return itemsCache;
}

const json = (status, body) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store" },
  });

// budget: 0 이상 숫자 또는 null, term: "5-2" 같은 값 또는 ""
function readConditions(body) {
  const budget = body?.budget ?? null;
  const term = body?.term ?? "";
  if (budget !== null && !(typeof budget === "number" && Number.isFinite(budget) && budget >= 0)) return null;
  if (typeof term !== "string" || (term !== "" && !/^\d{1,2}-\d{1,2}$/.test(term))) return null;
  return { budget, term };
}

async function askGemini(apiKey, conditions, candidates) {
  const input = JSON.stringify({
    조건: {
      예산: conditions.budget === null ? "제한 없음" : conditions.budget + "원 이하",
      "학년-학기": conditions.term || "전체",
    },
    후보: candidates.map(({ name, price, sales_point, publisher }) => ({ name, price, sales_point, publisher })),
  });

  const res = await fetch(ENDPOINT, {
    method: "POST",
    headers: {
      "x-goog-api-key": apiKey,
      "Content-Type": "application/json",
      "Api-Revision": API_REVISION,
    },
    body: JSON.stringify({
      model: MODEL,
      system_instruction: SYSTEM_INSTRUCTION,
      input: "아래 조건과 후보 표를 보고, 후보 중 한 권을 골라 이름과 이유 두 줄을 답해라.\n" + input,
      generation_config: { temperature: 0 },
      response_format: {
        type: "text",
        mime_type: "application/json",
        schema: {
          type: "object",
          properties: {
            name: { type: "string", enum: candidates.map((c) => c.name), description: "후보 표의 name 그대로" },
            reasons: { type: "array", items: { type: "string" }, minItems: 2, maxItems: 2, description: "이유 두 줄" },
          },
          required: ["name", "reasons"],
        },
      },
      store: false,
    }),
    signal: AbortSignal.timeout(25000),
  });
  if (!res.ok) throw new Error("gemini http " + res.status);

  const data = await res.json();
  const outputs = (data.steps || []).filter((s) => s.type === "model_output");
  const last = outputs[outputs.length - 1];
  const text = (last?.content || []).filter((c) => c.type === "text").map((c) => c.text).join("");
  if (!text) throw new Error("gemini empty");
  return JSON.parse(text);
}

export default {
  async fetch(request) {
    if (request.method !== "POST") return json(405, { error: "method_not_allowed" });

    let body;
    try {
      body = await request.json();
    } catch {
      return json(400, { error: "bad_request" });
    }
    const conditions = readConditions(body);
    if (!conditions) return json(400, { error: "bad_request" });

    const candidates = candidatesFor(await loadItems(), conditions.budget, conditions.term);
    if (candidates.length === 0) return json(200, { error: "no_candidates" });

    const apiKey = process.env.GEMINI_API_KEY;
    if (!apiKey) return json(503, { error: "ai_unavailable" });

    try {
      const answer = await askGemini(apiKey, conditions, candidates);
      return json(200, { name: answer?.name, reasons: answer?.reasons });
    } catch (err) {
      console.error("recommend:", err.message);
      return json(502, { error: "ai_unavailable" });
    }
  },
};
