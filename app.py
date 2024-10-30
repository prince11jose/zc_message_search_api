from flask import Flask, request, jsonify
from api import ZohoCliqAPI
from config import load_config, setup_logging
import logging

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)

app = Flask(__name__)
zoho_api = ZohoCliqAPI()

@app.route('/search_and_post', methods=['POST'])
def search_and_post():
    logger.info("Received a request to /search_and_post endpoint")
    
    search_query = request.json.get("search_query")

    if not search_query:
        logger.warning("Parameter 'search_query' is missing")
        return jsonify({"error": "Parameter 'search_query' is required"}), 400

    try:
        logger.info(f"Searching messages with query: {search_query}")
        search_results = zoho_api.search_messages(search_query)
        messages = search_results.get("data", {}).get("messages", [])
        logger.debug(f"Search results: {messages}")

        message_data = [{"chid": msg["chid"], "text": msg.get("message", msg.get("fcomment", ""))} for msg in messages]
        
        post_responses = []
        for data in message_data:
            if data["text"]:
                logger.info(f"Analyzing text: {data['text']}")
                analysis = zoho_api.analyze_text(data["text"])
                logger.debug(f"Analysis result: {analysis}")

                if analysis.get("result") == "Positive" and analysis.get("score") == 1.0:
                    logger.info(f"Posting message to chid: {data['chid']}")
                    post_response = zoho_api.post_message(data["chid"])
                    post_responses.append({"chid": data["chid"], "post_response": post_response})
                    logger.debug(f"Post response: {post_response}")

        return jsonify(post_responses)
    
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    logger.info("Starting Flask application")
    app.run(port=5000)
