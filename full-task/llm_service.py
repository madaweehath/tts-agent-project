import time
import json
import traceback
from openai import OpenAI
from config import OPENAI_API_KEY, MODEL_GENERATOR, MODEL_VALIDATOR, MODEL_CLASSIFIER, MAX_RETRIES

# ============ Initialize OpenAI Client ============
openai_client = None
try:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
    print("OpenAI client initialized")
except Exception as e:
    print(f"Error initializing OpenAI: {e}")


# ============ Helper Functions (Updated) ============

def call_openai_llm(system_prompt, user_prompt, model, is_json_mode=False):
    """Unified function for calling OpenAI Chat Completions (using provided logic)"""

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

        if is_json_mode:
            params["response_format"] = {"type": "json_object"}

        chat_completion = openai_client.chat.completions.create(**params)

        return chat_completion.choices[0].message.content

    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return None


# --- MODIFICATION: New news_classifier_agent function (Copied from colleague's code) ---
def news_classifier_agent(title: str, description: str):
    """
    Agent يصنف الخبر إلى جاد (1) أو عادي (0) باستخدام LLM.
    """
    if not title or not description or not openai_client:
        return "UNKNOWN"  # Changed from 'client' to 'openai_client'

    # Use the unified call_openai_llm
    client = openai_client

    system_prompt_classify = (
        "أنت مصنف محترف للأخبار. مهمتك هي تحليل العنوان والمحتوى وتحديد ما إذا كان الخبر:\n"
        "- 'جادة': أخبار سياسية، اقتصادية، أمنية، صحية مهمة، قرارات حكومية، أحداث عالمية مؤثرة\n"
        "- 'عادية': أخبار ثقافية، ترفيهية، رياضية، حياتية، تقنية غير حرجة، مقالات رأي\n"
        " اركز للجادة ب 1 والعادية ب0"
        "يجب أن ترد بتنسيق JSON فقط: {\"classification\": 0} أو {\"classification\": 1}\n"
        "لا تكتب أي شيء آخر."
    )

    user_prompt_classify = f"العنوان: {title}\n\nالمحتوى: {description[:500]}..."

    classification_response = call_openai_llm(  # Using the unified LLM caller
        system_prompt_classify,
        user_prompt_classify,
        MODEL_CLASSIFIER,
        is_json_mode=True
    )

    if not classification_response:
        print("  فشل في التصنيف")
        return "UNKNOWN"

    try:
        if classification_response.startswith("```json"):
            classification_response = classification_response[7:-3].strip()

        classification_json = json.loads(classification_response)
        # Return 0 or 1, or UNKNOWN if key is missing/invalid
        news_class = classification_json.get("classification", "UNKNOWN")

        print(f"  [المصنف] النتيجة: {news_class}")
        return news_class

    except json.JSONDecodeError as e:
        print(f"  فشل تحليل JSON من المصنف: {e}")
        return "UNKNOWN"


# ============ Main Conversion Function (Updated) ============

def convert_to_saudi_dialect(fusha_text: str):
    """Convert Fusha Arabic to Saudi dialect using generation + validation (using colleague's logic)"""

    if not openai_client:
        return "ERROR: OpenAI client not initialized"

    current_retries = 0
    generated_text = ""

    while current_retries < MAX_RETRIES:
        print(f"  [Agent 2] معالجة: {fusha_text[:40]}... (محاولة {current_retries + 1}/{MAX_RETRIES})")

        # Generation Step (Podcast Agent Logic)
        system_prompt_generate = (
            "أنت مذيع بودكاست عربي متخصص في تبسيط الأخبار."
            "مهمتك هي تحويل النص الفصيح التالي إلى لهجة نجدية سهلة ومفهومة للجميع،"
            "بأسلوب شيق وجذاب وكأنك تسولف."
            "لا تضف أي مقدمات أو خواتيم، فقط النص المحول."
        )
        user_prompt_generate = f"حول هذا النص: \n\n{fusha_text}"

        generated_text = call_openai_llm(
            system_prompt_generate,
            user_prompt_generate,
            MODEL_GENERATOR
        )

        if not generated_text:
            print(" فشل التوليد (LLM 1). جاري إعادة المحاولة...")
            current_retries += 1
            time.sleep(1)
            continue

        # Validation Step (Podcast Agent Logic)
        system_prompt_validate = (
            "أنت مدقق لغوي سريع. مهمتك هي تقييم النص المُعطى."
            "هل هو مكتوب بشكل عام بلهجة نجدية عامية مفهومة؟ أم أنه لا يزال (فصحى بالكامل)؟"
            "يجب أن ترد بتنسيق JSON حصراً. لا تكتب أي شيء آخر."
            "التنسيق المطلوب هو: {\"is_najde\": true} إذا كان النص عامياً."
            "أو {\"is_najde\": false} فقط إذا كان النص لا يزال (فصحى) ولم يتم تحويله."
        )
        user_prompt_validate = f"الرجاء تقييم هذا النص: \n\n{generated_text}"

        validation_response_str = call_openai_llm(
            system_prompt_validate,
            user_prompt_validate,
            MODEL_VALIDATOR,
            is_json_mode=True
        )

        if not validation_response_str:
            print("فشل التدقيق (LLM 2). جاري إعادة المحاولة...")
            current_retries += 1
            time.sleep(1)
            continue

        try:
            if validation_response_str.startswith("```json"):
                validation_response_str = validation_response_str[7:-3].strip()

            validation_json = json.loads(validation_response_str)
            is_najde = validation_json.get("is_najde")

            if is_najde is True:
                print(" Done نجح التحقق (لهجة نجدية).")
                return generated_text
            else:
                print("  Fail فشل التحقق (ليست لهجة نجدية). جاري إعادة التوليد...")
                current_retries += 1

        except json.JSONDecodeError as e:
            print(f"  fail فشل تحليل JSON من المدقق: {e}. جاري إعادة المحاولة...")
            current_retries += 1

    # Final failure
    print(f" drop  فشل نهائي في معالجة النص: {fusha_text[:50]}...")
    return "FAILED_GENERATION"