from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import List, Dict
import torch

#MODEL_NAME = "Qwen/Qwen2.5-3B-Instruct" # too huge
#MODEL_NAME = "microsoft/Phi-3-mini-4k-instruct" # smaller
MODEL_NAME = "HuggingFaceTB/SmolLM2-135M-Instruct"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
model.eval() 

SESSIONS: Dict[str, List[dict]] = {}
SYSTEM_PROMPT = "You are helpful assistant. Answer in english. No hallocinations. If you don't know, just say you don't know."
history = [{"role": "system", "content": SYSTEM_PROMPT}]

if tokenizer.pad_token_id is None:
    tokenizer.pad_token = tokenizer.eos_token
eos_id = tokenizer.eos_token_id
pad_id = tokenizer.pad_token_id
MAX_TURNS = 4  # when the history id too long (more than MAX_TURNS turns), cut it


def clamp_history(history):
    if not history:
        return []
    sys = history[0:1] if history and history[0]["role"] == "system" else []
    rest = history[1:] if sys else history
    trimmed = rest[-MAX_TURNS*2:]
    return sys + trimmed


def get_history(session_id: str) -> List[dict]:
    if session_id not in SESSIONS:
        SESSIONS[session_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    return SESSIONS[session_id]


def chat_once(history: List[dict], user_text: str, max_new_tokens=256, temperature=0.75) -> str:
    history.append({"role": "user", "content": user_text})
    safe_history = clamp_history(history)
    inputs = tokenizer.apply_chat_template(
        safe_history,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True, return_tensors="pt",
    )

    with torch.inference_mode():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=True
        )

    prompt_len = inputs["input_ids"].shape[1]
    gen_ids = outputs[0][prompt_len:] if outputs[0].size(0) > prompt_len else outputs[0]
    text = tokenizer.decode(gen_ids, skip_special_tokens=True).strip()

    history.append({"role": "assistant", "content": text})
    return text
