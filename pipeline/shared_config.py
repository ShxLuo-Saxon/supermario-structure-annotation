"""Shared configuration for Gemini API scripts."""
import pathlib
from google import genai

# Repo root (one level up from pipeline/)
_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent

# Alternatives: "gemini-3-flash-preview", "gemini-3-pro-preview"
MODEL_ID = "gemini-3.1-pro-preview"

PROMPT_PATH = _REPO_ROOT / "pipeline" / "prompts" / "prompt_v1.2.md"

def get_response_schema():
    """Return the shared JSON response schema for annotation tasks."""
    return genai.types.Schema(
        type=genai.types.Type.OBJECT,
        required=["Tile", "IsAdaptive", "IsStinger", "Function", "Section"],
        properties={
            "Tile": genai.types.Schema(
                type=genai.types.Type.STRING,
            ),
            "IsAdaptive": genai.types.Schema(
                type=genai.types.Type.BOOLEAN,
            ),
            "IsStinger": genai.types.Schema(
                type=genai.types.Type.BOOLEAN,
            ),
            "Function": genai.types.Schema(
                type=genai.types.Type.ARRAY,
                items=genai.types.Schema(
                    type=genai.types.Type.OBJECT,
                    required=["BarRange", "Function"],
                    properties={
                        "BarRange": genai.types.Schema(
                            type=genai.types.Type.ARRAY,
                            items=genai.types.Schema(
                                type=genai.types.Type.INTEGER,
                            ),
                        ),
                        "Function": genai.types.Schema(
                            type=genai.types.Type.STRING,
                        ),
                        "Inference": genai.types.Schema(
                            type=genai.types.Type.STRING,
                        ),
                    },
                ),
            ),
            "Section": genai.types.Schema(
                type=genai.types.Type.ARRAY,
                items=genai.types.Schema(
                    type=genai.types.Type.OBJECT,
                    required=["BarRange", "Function", "Section"],
                    properties={
                        "BarRange": genai.types.Schema(
                            type=genai.types.Type.ARRAY,
                            items=genai.types.Schema(
                                type=genai.types.Type.INTEGER,
                            ),
                        ),
                        "Function": genai.types.Schema(
                            type=genai.types.Type.STRING,
                        ),
                        "Section": genai.types.Schema(
                            type=genai.types.Type.STRING,
                        ),
                        "Inference": genai.types.Schema(
                            type=genai.types.Type.STRING,
                        ),
                    },
                ),
            ),
        },
    )

def load_system_instruction(path=None):
    """Load system instruction text from the prompt file."""
    prompt_path = path or PROMPT_PATH
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()
