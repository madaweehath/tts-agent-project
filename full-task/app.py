import uuid
from email.utils import parsedate_to_datetime

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import traceback
from datetime import datetime, timezone

# Import all services
from config import OUTPUT_DIR
from llm_service import openai_client, convert_to_saudi_dialect, news_classifier_agent
from tts_service import initialize_tts, generate_audio, is_tts_ready
from scraper_service import scrape_alriyadh_news
from storage_service import gcs_client, upload_to_gcs, get_audio_duration, cleanup_local_files

# ============ Flask Setup ============
app = Flask(__name__)
CORS(app)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============ API Endpoints ============

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
            "status": "healthy",
            "service": "agent_service",
            "llm_ready": openai_client is not None,
            "tts_ready": is_tts_ready(),
            "gcs_ready": gcs_client is not None
        })

@app.route('/api/scrape-news', methods=['GET'])
def scrape_news():
    """Scrape latest news from AlRiyadh"""
    try:
        print("\n" + "="*50)
        print("Scrape endpoint called")
        print("="*50)
        news_data = scrape_alriyadh_news()
        return jsonify({
            "success": True,
            "count": len(news_data),
            "articles": news_data
        })
    except Exception as e:
        print(f"Error in scrape endpoint: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/convert-to-dialect', methods=['POST'])
def convert_to_dialect_endpoint():
    """Convert Fusha text to Saudi dialect"""
    try:
        data = request.get_json()
        fusha_text = data.get('text', '')

        if not fusha_text:
            return jsonify({"success": False, "error": "No text provided"}), 400

        dialect_text = convert_to_saudi_dialect(fusha_text)

        if not dialect_text or "ERROR" in dialect_text:
            return jsonify({"success": False, "error": dialect_text}), 500

        return jsonify({
            "success": True,
            "original": fusha_text[:100] + "..." if len(fusha_text) > 100 else fusha_text,
            "dialect": dialect_text
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/generate-audio', methods=['POST'])
def generate_audio_endpoint():
    """Generate audio from text"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        output_name = data.get('name', None)

        if not text:
            return jsonify({"success": False, "error": "No text provided"}), 400

        audio_path, duration = generate_audio(text, output_name)

        if audio_path:
            return jsonify({
                "success": True,
                "audio_path": audio_path,
                "duration": duration  # Already calculated!
            })

        else:
            return jsonify({"success": False, "error": "Audio generation failed"}), 500

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/scrape-and-convert', methods=['GET'])
def scrape_and_convert():
    """
    1. Scrapes news from AlRiyadh.
    2. Converts the full article text from Fusha to Saudi Dialect.
    3. Returns the enriched data.
    """
    print("\n" + "=" * 50)
    print("Scrape-and-Convert endpoint called (Now processing full text!)")
    print("=" * 50)

    try:
        # 1. SCRAPING PHASE
        scraped_articles = scrape_alriyadh_news()  # Assuming this now returns the detailed JSON above

        if not scraped_articles:
            return jsonify({
                "success": False,
                "message": "Scraping completed, but no articles were found."
            }), 200

        processed_articles = []

        # 2. ITERATION & CONVERSION PHASE
        for article in scraped_articles:
            # *** CRITICAL CHANGE: Using the correct key from the scraper's output ***
            fusha_text_to_convert = article.get('description_fusha', '')

            title = article.get('title', 'Untitled')
            link = article.get('link')

            # Retrieve the conversion function, which includes LLM calls and validation
            if fusha_text_to_convert:
                print(f"-> Converting text for article: {title[:30]}...")

                # Call the LLM-based dialect conversion function
                dialect_text = convert_to_saudi_dialect(fusha_text_to_convert)

                # 3. Create a new, enriched article dictionary
                processed_articles.append({
                    "title": title,
                    "link": link,
                    "original_fusha_full_text": fusha_text_to_convert,
                    "saudi_dialect_full_text": dialect_text
                })
            else:
                # If, for some reason, the text is still missing
                processed_articles.append({
                    "title": title,
                    "link": link,
                    "original_fusha_full_text": "",
                    "saudi_dialect_full_text": "No text found for conversion."
                })

        # 4. FINAL RESPONSE
        return jsonify({
            "success": True,
            "message": "News scraped and full articles converted to Saudi dialect.",
            "count": len(processed_articles),
            "articles": processed_articles
        })

    except Exception as e:
        print(f"Critical Error in scrape-and-convert endpoint: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/scrape-and-process-all', methods=['POST'])
def scrape_and_process_all():
    """
    Complete automated pipeline:
    1. Scrape news from AlRiyadh
    2. For each article: Convert to dialect + Generate audio + Upload to GCS
    3. Return array of episode JSON ready for EpisodeAutomationService
    """
    try:
        print("\n" + "=" * 60)
        print("Full Automated Pipeline Started")
        print("=" * 60)

        # Step 1: Scrape news
        print("Step 1: Scraping news from AlRiyadh...")
        news_articles = scrape_alriyadh_news()

        if not news_articles:
            return jsonify({
                "success": False,
                "error": "No articles scraped"
            }), 404

        print(f"Scraped {len(news_articles)} articles")

        # Step 2: Process each article
        processed_episodes = []

        for idx, article in enumerate(news_articles, 1):
            try:
                print(f"\n--- Processing Article {idx}/{len(news_articles)} ---")
                print(f"Title: {article['title'][:50]}...")

                title = article['title']
                fusha_text = article['description_fusha']
                publication_date = article['date']
                if publication_date:
                    dt = parsedate_to_datetime(publication_date)
                    publication_date = dt.isoformat()

                print("Classifying article...")
                classification_result = news_classifier_agent(title, fusha_text)

                # Determine voice type: '1' (Serious) maps to 'serious', '0' (Normal/Default) maps to 'normal'
                voice_type = 'serious' if classification_result == 1 else 'normal'
                print(f"Classification: {classification_result} -> Voice: {voice_type}")

                # Convert to dialect
                print("Converting to Saudi dialect...")
                dialect_script = convert_to_saudi_dialect(fusha_text)

                if not dialect_script or "ERROR" in dialect_script:
                    print(f"Skipping article (LLM failed)")
                    continue

                # Generate audio
                print(f"Generating audio with **{voice_type.upper()}** voice...")
                audio_filename = f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}_{voice_type}"
                audio_path, audio_duration = generate_audio(dialect_script, audio_filename, voice_type=voice_type)

                if not audio_path:
                    print(f"Skipping article (TTS failed)")
                    continue

                print(f"Duration: {audio_duration} seconds")

                # Save script to file
                print("Saving script...")
                script_filename = f"{audio_filename}_script.txt"
                script_path = os.path.join(OUTPUT_DIR, script_filename)
                with open(script_path, 'w', encoding='utf-8') as f:
                    f.write(dialect_script)

                # Save original content to file
                content_filename = f"{audio_filename}_original.txt"
                content_path = os.path.join(OUTPUT_DIR, content_filename)
                with open(content_path, 'w', encoding='utf-8') as f:
                    f.write(fusha_text)

                # Upload to GCS
                print("Uploading to Google Cloud Storage...")
                audio_gcs_url = upload_to_gcs(
                    audio_path,
                    f"audio/{audio_filename}.wav"
                )
                script_gcs_url = upload_to_gcs(
                    script_path,
                    f"scripts/{script_filename}"
                )
                content_gcs_url = upload_to_gcs(
                    content_path,
                    f"content/{content_filename}"
                )

                # Cleanup local files
                cleanup_local_files(audio_path, script_path, content_path)

                # Build episode JSON
                episode_json = {
                    "article": {
                        "title": title,
                        "category": "news",
                        "author": None,
                        "publisher": "AlRiyadh",
                        "publicationDate": publication_date,
                        "contentRawUrl": content_gcs_url,
                        "scriptUrl": script_gcs_url
                    },
                    "audio": {
                        "duration": audio_duration,
                        "format": "wav",
                        "urlPath": audio_gcs_url
                    },
                    "episode": {
                        "title": title,
                        "description": f"بودكاست: {title}",
                        "scriptUrlPath": script_gcs_url,
                        "imageUrl": "https://i.imgur.com/Lt65Eso.png"
                    }
                }

                processed_episodes.append(episode_json)
                print(f"Article {idx} processed successfully")

            except Exception as e:
                print(f"Error processing article {idx}: {e}")
                traceback.print_exc()
                continue

        print("\n" + "=" * 60)
        print(f"Pipeline Complete: {len(processed_episodes)}/{len(news_articles)} episodes created")
        print("=" * 60 + "\n")

        return jsonify({
            "success": True,
            "total_scraped": len(news_articles),
            "total_processed": len(processed_episodes),
            "episodes": processed_episodes
        })

    except Exception as e:
        print(f"Error in automated pipeline: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("Starting Agent Service on http://localhost:8001")
    print("=" * 60)

    if openai_client:
        print("LLM client ready")
    else:
        print("WARNING: LLM client NOT initialized!")

    tts_ready = initialize_tts()
    if is_tts_ready():  # Check using the new function
        print("TTS models ready")
    else:
        print("WARNING: TTS models NOT fully initialized!")

    print("=" * 60 + "\n")

    app.run(host='0.0.0.0', port=8001, debug=True, use_reloader=False)