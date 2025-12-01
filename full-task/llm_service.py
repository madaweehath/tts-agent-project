import time
import json
import traceback
from openai import OpenAI
from config import OPENAI_API_KEY, MODEL_GENERATOR, MODEL_VALIDATOR, MAX_RETRIES

# ============ Initialize OpenAI Client ============
openai_client = None
try:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
    print("✓ OpenAI client initialized")
except Exception as e:
    print(f"✗ Error initializing OpenAI: {e}")

# ============ Helper Functions ============

def call_openai_llm(system_prompt, user_prompt, model, is_json_mode=False):

    if not openai_client:
        print("Error: OpenAI client not initialized.")
        return None
        
    try:
        params = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 4096,
            "top_p": 0.95,
            "stream": False
        }

        # Only add response_format if JSON mode is requested
        if is_json_mode:
            params["response_format"] = {"type": "json_object"}

        chat_completion = openai_client.chat.completions.create(**params)

        return chat_completion.choices[0].message.content

    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return None


# ============ Main Conversion Function ============

def convert_to_saudi_dialect(fusha_text: str):
    """Convert Fusha Arabic to Saudi dialect using generation + validation"""

    if not openai_client:
        return "ERROR: OpenAI client not initialized"
    
    current_retries = 0
    
    # while current_retries < MAX_RETRIES:
    print(f"  Processing attempt {current_retries + 1}/{MAX_RETRIES}")

    # ---- Generation Step ----
    system_prompt_generate = (
        "أنت مذيع بودكاست عربي متخصص في تبسيط الأخبار بلغة سهلة ولهجة سعودية واضحة."
    )
    user_prompt_generate = f"حوّل هذا النص إلى لهجة سعودية واضحة:\n\n{fusha_text}"
    
    generated_text = call_openai_llm(
        system_prompt_generate,
        user_prompt_generate,
        MODEL_GENERATOR
    )
    
        # if not generated_text:
        #     current_retries += 1
        #     time.sleep(1)
        #     continue
    print("  ✓ Generation successful")
    return generated_text

        
    #     # ---- Validation Step ----
    #     system_prompt_validate = (
    #         "أنت مدقق لغوي. قيّم هل النص المكتوب باللهجة السعودية صحيح وطبيعي."
    #     )
    #     user_prompt_validate = f"""
    #     قيّم النص التالي وأرجع النتيجة بصيغة JSON فقط.

    #     النص:
    #     {generated_text}

    #     يجب أن يكون الإخراج بهذا الشكل:
    #     {{
    #     "is_bayda": true/false
    #     }}
    #     """

    #     validation_response = call_openai_llm(
    #         system_prompt_validate,
    #         user_prompt_validate,
    #         MODEL_VALIDATOR,
    #         is_json_mode=True
    #     )

    #     if not validation_response:
    #         current_retries += 1
    #         time.sleep(1)
    #         continue
        
    #     try:
    #         if validation_response.startswith("```json"):
    #             validation_response = validation_response[7:-3].strip()
            
    #         validation_json = json.loads(validation_response)
    #         is_bayda = validation_json.get("is_bayda")
            
    #         if is_bayda is True:
    #             print("  ✓ Validation successful")
    #             return generated_text
    #         else:
    #             print("  ✗ Validation failed, retrying...")
    #             current_retries += 1
                
    #     except json.JSONDecodeError as e:
    #         print(f"  JSON decode error: {e}")
    #         current_retries += 1
    
    # return "FAILED_GENERATION"
