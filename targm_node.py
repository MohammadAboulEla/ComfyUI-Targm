import folder_paths
import os
import torch

SUPPORTED_LANGUAGES = [
    "English",
    "Arabic",
    "Bengali",
    "Burmese",
    "Chinese",
    "Czech",
    "Dutch",
    "French",
    "German",
    "Gujarati",
    "Hebrew",
    "Hindi",
    "Indonesian",
    "Italian",
    "Japanese",
    "Kazakh",
    "Khmer",
    "Korean",
    "Malay",
    "Marathi",
    "Mongolian",
    "Persian",
    "Polish",
    "Portuguese",
    "Russian",
    "Spanish",
    "Tagalog",
    "Tamil",
    "Telugu",
    "Thai",
    "Tibetan",
    "Turkish",
    "Ukrainian",
    "Urdu",
    "Uyghur",
    "Vietnamese",
]

# Cached model/tokenizer to avoid reloading on every run
_model = None
_tokenizer = None

MODEL_REPO = "tencent/HY-MT1.5-1.8B-FP8"


def get_model_dir():
    # Store model under ComfyUI's models directory
    base = folder_paths.models_dir
    return os.path.join(base, "targm", "HY-MT1.5-1.8B-FP8")


def load_model():
    global _model, _tokenizer
    if _model is not None:
        return _model, _tokenizer

    from transformers import AutoModelForCausalLM, AutoTokenizer

    model_dir = get_model_dir()

    # Download if missing
    if not os.path.exists(model_dir):
        os.makedirs(model_dir, exist_ok=True)
        print(f"[Targm] Downloading model {MODEL_REPO} to {model_dir} ...")
        from huggingface_hub import snapshot_download

        snapshot_download(
            repo_id=MODEL_REPO,
            local_dir=model_dir,
            local_dir_use_symlinks=False,
        )

    print(f"[Targm] Loading model from {model_dir} ...")
    _tokenizer = AutoTokenizer.from_pretrained(model_dir)
    _model = AutoModelForCausalLM.from_pretrained(
        model_dir,
        device_map="auto",
        dtype=torch.bfloat16,  # recommended for performance
    )
    return _model, _tokenizer


class Targm:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": ""}),
                "target_language": (SUPPORTED_LANGUAGES, {"default": "English"}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xFFFFF}),
            },
            "hidden": {
                "max_new_tokens": (
                    "INT",
                    {"default": 2048, "min": 64, "max": 4096, "step": 64, "tooltip": "Maximum new tokens to generate."},
                ),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("translated_text",)
    FUNCTION = "translate"
    CATEGORY = "Targm"

    def translate(
        self, text: str, target_language: str = "English", seed: int = 0, max_new_tokens: int = 2048
    ):
        torch.manual_seed(seed)  # reproducible output
        model, tokenizer = load_model()

        messages = [
            {
                "role": "user",
                "content": (
                    f"Translate the following segment into {target_language}, "
                    f"without additional explanation.\n\n{text}"
                ),
            }
        ]

        tokenized_chat = tokenizer.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=False,
            return_tensors="pt",
        )

        with torch.no_grad():
            outputs = model.generate(
                tokenized_chat.to(model.device),
                max_new_tokens=max_new_tokens,
            )

        # Decode only the newly generated tokens
        input_length = tokenized_chat.shape[1]
        translated = tokenizer.decode(
            outputs[0][input_length:],
            skip_special_tokens=True,
        )

        return (translated,)


NODE_CLASS_MAPPINGS = {
    "TARGM": Targm,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TARGM": "Translate",
}
