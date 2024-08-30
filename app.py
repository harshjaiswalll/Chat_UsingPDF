from flask import Flask, request, jsonify, send_from_directory
import boto3
import json
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
import boto3
from requests_aws4auth import AWS4Auth
app = Flask(__name__, static_url_path='', static_folder='.')

region = "us-west-2"
bedrock_client = boto3.client("bedrock-runtime", 
                    region_name=region,
                    aws_access_key_id="",
                    aws_secret_access_key="")

model_id = "mistral.mixtral-8x7b-instruct-v0:1"

host = '7i5eknycs53e9kp1qlo8.us-west-2.aoss.amazonaws.com' # cluster endpoint, for example: my-test-domain.us-east-1.es.amazonaws.com
region = 'us-west-2'
service = 'aoss'
#credentials = boto3.Session().get_credentials()
auth = AWS4Auth("","", region, service)

client = OpenSearch(
     hosts = [{'host': host, 'port': 443}],
    http_auth = auth,
    use_ssl = True,
    verify_certs = True,
    connection_class = RequestsHttpConnection,
    pool_maxsize = 20
)

@app.route('/')
def index():
    return send_from_directory('template', 'index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    
    def text_embedding(text):
        body=json.dumps({"inputText": text})
        response = bedrock_client.invoke_model(body=body, modelId='amazon.titan-embed-text-v1', accept='application/json', contentType='application/json')
        response_body = json.loads(response.get('body').read())
        embedding = response_body.get('embedding')
        return embedding
    try:
        data = request.get_json()
        question = data['question']

        vector=text_embedding(question)
        print(len(vector))
        document = {
        "size": 4,
        "query": {
        "script_score": {
        "query": {
        "match_all": {}
        },
        "script": {
        "source": "knn_score",
        "lang": "knn",
        "params": {
            "field": "test_vector",
            "query_value": vector,
            "space_type": "cosinesimil"
        }
        }
        }
        }
        }

        response = client.search(
            body = document,
            index = "testindex"
        )

        print(response)
        paragraph= ''
        hits = response['hits']['hits']
        for hit in hits:
            document_text = hit['_source']['document_text']
            #print(document_text)
            paragraph += document_text

        print(paragraph)      
        prompt = f"<s>You find the answer of given paragraph or statment</s>[INST] {paragraph} [/INST][INST]{question}[/INST]"
            #prompt = f"<s>[INST] {question} [/INST]"

        body = json.dumps({
            "prompt": prompt,
            "max_tokens": 1024,
            "top_p": 0.8,
            "temperature": 0.5,
        })

        response = bedrock_client.invoke_model(
            modelId=model_id,
            accept="application/json",
            contentType="application/json",
            body=body,
        )

        response_body = json.loads(response['body'].read().decode())
        output_text = response_body["outputs"][0]["text"]
        return jsonify({'response': output_text})

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
