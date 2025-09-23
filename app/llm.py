import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from app.session_manager import get_session_history

# MODEL_NAME = "Qwen/Qwen2.5-3B-Instruct" # too huge
# MODEL_NAME = "microsoft/Phi-3-mini-4k-instruct" # smaller
MODEL_NAME = "HuggingFaceTB/SmolLM2-135M-Instruct"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
model.eval()


def chat_once(session_id: str, user_text: str, max_new_tokens=100, temperature=0.1) -> str:
    """single chat with AI assistant"""
    history = get_session_history(session_id)
    history.append({"role": "user", "content": user_text})
    inputs = tokenizer.apply_chat_template(
        history,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True, return_tensors="pt",
    )
    with torch.inference_mode():
        outputs = model.generate(
            **inputs,  # or input_ids=inputs["input_ids"], attention_mask=inputs["attention_mask"],
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=temperature
        )

    prompt_len = inputs["input_ids"].shape[1]  # length of the response
    gen_ids = outputs[0][prompt_len:] if outputs[0].size(0) > prompt_len else outputs[0]
    # remove prompt form the resopnse
    text = tokenizer.decode(gen_ids, skip_special_tokens=True).strip()
    # Change tokens z gen_ids to text. skip_special_tokens=True removes <s> itp.
    history.append({"role": "assistant", "content": text})
    return text
